import os
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

from flask import (
    Flask,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from fpdf import FPDF
from ultralytics import YOLO
import pandas as pd
import cv2
from threading import Lock

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
EXCEL_DIR = BASE_DIR / "outputs" / "excel"
PDF_DIR = BASE_DIR / "outputs" / "pdf"
STATIC_DIR = BASE_DIR / "static"

for folder in [UPLOAD_DIR, EXCEL_DIR, PDF_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "biomas_secret_key")

analysis_lock = threading.Lock()
analysis_state = {
    "running": False,
    "status": "idle",
    "message": "Lista para analizar",
    "progress": 0,
    "started_at": None,
    "finished_at": None,
    "result": None,
    "cancel_requested": False,
}

MODEL = None

latest_frame = None
frame_lock = Lock()


def get_model():
    global MODEL
    if MODEL is None:
        MODEL = YOLO("yolov8n.pt")
    return MODEL


def xywh_to_xyxy(box):
    x, y, w, h = box
    return [x - w / 2, y - h / 2, x + w / 2, y + h / 2]


def compute_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interW = max(0.0, xB - xA)
    interH = max(0.0, yB - yA)
    interArea = interW * interH
    if interArea == 0:
        return 0.0
    boxAArea = max(0.0, boxA[2] - boxA[0]) * max(0.0, boxA[3] - boxA[1])
    boxBArea = max(0.0, boxB[2] - boxB[0]) * max(0.0, boxB[3] - boxB[1])
    return interArea / float(boxAArea + boxBArea - interArea)


def save_excel(summary, detections, tracked_objects, metadata, file_name):
    file_path = EXCEL_DIR / file_name
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        pd.DataFrame(summary).to_excel(writer, sheet_name="Resumen", index=False)
        pd.DataFrame(detections).to_excel(writer, sheet_name="Detecciones", index=False)
        pd.DataFrame(tracked_objects).to_excel(writer, sheet_name="Objetos", index=False)
        pd.DataFrame([metadata]).to_excel(writer, sheet_name="Metadata", index=False)
    return file_path


def save_pdf(summary, file_name, source_description, metadata):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 12, "Informe de Análisis de Video", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 8, f"Fuente: {source_description}", ln=True)
    pdf.cell(0, 8, f"Estado: {analysis_state['status']}", ln=True)
    pdf.cell(0, 8, "Objetivo: Cajas 3x5 cm", ln=True)
    pdf.ln(4)

    for key, value in metadata.items():
        pdf.cell(0, 8, f"{key}: {value}", ln=True)
    pdf.ln(4)

    total = sum(item["Conteo"] for item in summary)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Total de detecciones únicas: {total}", ln=True)
    pdf.ln(6)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(95, 8, "Clase", border=1)
    pdf.cell(95, 8, "Conteo", border=1, ln=True)
    pdf.set_font("Arial", "", 12)
    for item in summary:
        pdf.cell(95, 8, str(item["Clase"]), border=1)
        pdf.cell(95, 8, str(item["Conteo"]), border=1, ln=True)

    file_path = PDF_DIR / file_name
    pdf.output(str(file_path))
    return file_path


def is_3x5_box(box):
    if not box or len(box) < 4:
        return False
    width = float(box[2])
    height = float(box[3])
    if width <= 0 or height <= 0:
        return False
    ratio = width / height if width >= height else height / width
    return 1.4 <= ratio <= 1.9


def analyze_source(source, source_description):
    global latest_frame
    analysis_state["status"] = "analizando"
    analysis_state["message"] = "Cargando modelo YOLOv8..."
    analysis_state["progress"] = 0
    analysis_state["started_at"] = datetime.now().isoformat()
    analysis_state["finished_at"] = None
    analysis_state["result"] = None
    analysis_state["cancel_requested"] = False

    model = get_model()
    summary_counts = {}
    total_frames = 0
    tracked_objects = []
    next_object_id = 1
    object_ids_seen = set()
    box_3x5_ids = set()
    detections_log = []

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_name = f"analisis_{timestamp}.xlsx"
    pdf_name = f"informe_{timestamp}.pdf"
    metadata = {
        "Fuente": source_description,
        "Archivo": str(source) if isinstance(source, str) else "Cámara en vivo",
        "Archivo Excel": excel_name,
        "Archivo PDF": pdf_name,
    }

    analysis_state["message"] = "Ejecutando análisis de video..."
    try:
        results = model.predict(source=source, stream=True, verbose=False)
        save_every = 20
        last_save_frame = 0
        for result in results:
            if analysis_state["cancel_requested"]:
                analysis_state["message"] = "Análisis cancelado"
                break
            total_frames += 1
            # get annotated image (if available) and update latest_frame for streaming
            try:
                annotated = result.plot() if hasattr(result, "plot") else None
                if annotated is not None:
                    ret, jpeg = cv2.imencode('.jpg', annotated)
                    if ret:
                        with frame_lock:
                            latest_frame = jpeg.tobytes()
            except Exception:
                pass

            if result.boxes is not None and len(result.boxes) > 0:
                classes = result.boxes.cls.tolist() if hasattr(result.boxes, "cls") else []
                if hasattr(result.boxes, "xyxy"):
                    boxes_xyxy = result.boxes.xyxy.tolist()
                elif hasattr(result.boxes, "xywh"):
                    boxes_xyxy = [xywh_to_xyxy(box) for box in result.boxes.xywh.tolist()]
                else:
                    boxes_xyxy = []
                confidences = result.boxes.conf.tolist() if hasattr(result.boxes, "conf") else [0.0] * len(classes)

                for idx, cls in enumerate(classes):
                    label = model.names[int(cls)] if int(cls) in model.names else str(int(cls))
                    xyxy = boxes_xyxy[idx] if idx < len(boxes_xyxy) else [0.0, 0.0, 0.0, 0.0]
                    conf = float(confidences[idx]) if idx < len(confidences) else 0.0

                    matched_id = None
                    best_iou = 0.0
                    for obj in tracked_objects:
                        if obj["Clase"] != label:
                            continue
                        iou_value = compute_iou(obj["BBox"], xyxy)
                        if iou_value > best_iou:
                            best_iou = iou_value
                            matched_id = obj["ObjectID"]
                            matched_object = obj

                    if best_iou >= 0.35 and matched_id is not None:
                        matched_object["BBox"] = xyxy
                        matched_object["LastFrame"] = total_frames
                        matched_object["FramesDetectados"] += 1
                        matched_object["Confianza"] = conf
                        object_id = matched_id
                    else:
                        object_id = next_object_id
                        next_object_id += 1
                        tracked_objects.append(
                            {
                                "ObjectID": object_id,
                                "Clase": label,
                                "BBox": xyxy,
                                "FirstFrame": total_frames,
                                "LastFrame": total_frames,
                                "FramesDetectados": 1,
                                "Confianza": conf,
                            }
                        )

                    if object_id not in object_ids_seen:
                        object_ids_seen.add(object_id)
                        summary_counts[label] = summary_counts.get(label, 0) + 1

                    if is_3x5_box([xyxy[2] - xyxy[0], xyxy[3] - xyxy[1], xyxy[2] - xyxy[0], xyxy[3] - xyxy[1]]):
                        if object_id not in box_3x5_ids:
                            box_3x5_ids.add(object_id)
                            summary_counts["Caja 3x5 cm"] = summary_counts.get("Caja 3x5 cm", 0) + 1

                    detections_log.append(
                        {
                            "ObjectID": object_id,
                            "Clase": label,
                            "Confianza": conf,
                            "Frame": total_frames,
                            "X1": float(xyxy[0]),
                            "Y1": float(xyxy[1]),
                            "X2": float(xyxy[2]),
                            "Y2": float(xyxy[3]),
                        }
                    )

            if total_frames - last_save_frame >= save_every:
                current_summary = [
                    {"Clase": cls, "Conteo": count}
                    for cls, count in sorted(summary_counts.items(), key=lambda x: -x[1])
                ]
                if not current_summary:
                    current_summary = [{"Clase": "Ninguna detección", "Conteo": 0}]
                try:
                    save_excel(
                        current_summary,
                        detections_log,
                        tracked_objects,
                        {
                            **metadata,
                            "Frames analizados": total_frames,
                            "Objetos únicos": len(tracked_objects),
                            "Estado actual": analysis_state["status"],
                        },
                        excel_name,
                    )
                    save_pdf(
                        current_summary,
                        pdf_name,
                        source_description,
                        {
                            **metadata,
                            "Frames analizados": total_frames,
                            "Objetos únicos": len(tracked_objects),
                            "Estado actual": analysis_state["status"],
                        },
                    )
                except Exception:
                    pass
                last_save_frame = total_frames

            if total_frames % 10 == 0:
                analysis_state["progress"] = min(100, int(total_frames / 200 * 100))

        if analysis_state["cancel_requested"]:
            analysis_state["status"] = "cancelado"
            analysis_state["finished_at"] = datetime.now().isoformat()
            return
    except Exception as error:
        if str(error) == "Cancelado por el usuario":
            analysis_state["status"] = "cancelado"
            analysis_state["finished_at"] = datetime.now().isoformat()
            return
        analysis_state["status"] = "error"
        analysis_state["message"] = f"Error en el análisis: {error}"
        analysis_state["finished_at"] = datetime.now().isoformat()
        return

    summary = [{"Clase": cls, "Conteo": count} for cls, count in sorted(summary_counts.items(), key=lambda x: -x[1])]
    if not summary:
        summary = [{"Clase": "Ninguna detección", "Conteo": 0}]

    analysis_state["message"] = "Generando archivos de informe..."
    excel_path = save_excel(
        summary,
        detections_log,
        tracked_objects,
        {
            **metadata,
            "Frames analizados": total_frames,
            "Objetos únicos": len(tracked_objects),
            "Estado final": analysis_state["status"],
        },
        excel_name,
    )
    pdf_path = save_pdf(
        summary,
        pdf_name,
        source_description,
        {
            **metadata,
            "Frames analizados": total_frames,
            "Objetos únicos": len(tracked_objects),
            "Estado final": analysis_state["status"],
        },
    )

    analysis_state["status"] = "completado"
    analysis_state["message"] = "Análisis finalizado correctamente"
    analysis_state["progress"] = 100
    analysis_state["finished_at"] = datetime.now().isoformat()
    analysis_state["result"] = {
        "excel": excel_name,
        "pdf": pdf_name,
        "summary": summary,
        "frames": total_frames,
        "source": source_description,
        "objetos_unicos": len(tracked_objects),
    }


def generate_frame_stream():
    while True:
        with frame_lock:
            frame = latest_frame
        if frame is not None:
            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        else:
            time.sleep(0.05)


@app.route('/stream')
def stream():
    return Response(generate_frame_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start-analysis", methods=["POST"])
def start_analysis():
    if analysis_state["running"]:
        return jsonify({"success": False, "message": "Ya hay un análisis en ejecución."}), 409

    source_type = request.form.get("sourceType")
    source_value = request.form.get("sourceValue", "").strip()
    uploaded_file = request.files.get("videoFile")
    source = None
    source_description = ""

    if source_type == "upload":
        if not uploaded_file or uploaded_file.filename == "":
            return jsonify({"success": False, "message": "Selecciona un archivo de video."}), 400
        filename = f"upload_{uuid.uuid4().hex}_{uploaded_file.filename}"
        saved_path = UPLOAD_DIR / filename
        uploaded_file.save(saved_path)
        source = str(saved_path)
        source_description = f"Archivo local: {uploaded_file.filename}"
    elif source_type == "webcam":
        source = 0
        source_description = "Cámara web local"
    elif source_type == "url":
        if not source_value:
            return jsonify({"success": False, "message": "Proporciona la URL de la cámara."}), 400
        source = source_value
        source_description = f"Cámara web por URL: {source_value}"
    else:
        return jsonify({"success": False, "message": "Selecciona una fuente válida."}), 400

    def worker():
        with analysis_lock:
            analysis_state["running"] = True
            try:
                analyze_source(source, source_description)
            finally:
                analysis_state["running"] = False

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    return jsonify({"success": True, "message": "Análisis iniciado."})


@app.route("/stop-analysis", methods=["POST"])
def stop_analysis():
    if not analysis_state["running"]:
        return jsonify({"success": False, "message": "No hay análisis en curso."}), 400
    analysis_state["cancel_requested"] = True
    analysis_state["message"] = "Solicitud de parada enviada..."
    return jsonify({"success": True, "message": "Solicitud de parada enviada."})


@app.route("/cancel-all", methods=["POST"])
def cancel_all():
    analysis_state["cancel_requested"] = True
    analysis_state["message"] = "Cancelando todo..."
    return jsonify({"success": True, "message": "Cancelación solicitada."})


@app.route("/status")
def status():
    return jsonify(analysis_state)


@app.route("/files/list")
def list_files():
    file_type = request.args.get("type")
    if file_type == "excel":
        folder = EXCEL_DIR
    elif file_type == "pdf":
        folder = PDF_DIR
    else:
        return jsonify({"success": False, "message": "Tipo de archivo inválido."}), 400

    files = []
    for entry in sorted(folder.iterdir(), key=os.path.getmtime, reverse=True):
        if entry.is_file():
            files.append({
                "name": entry.name,
                "path": entry.name,
                "modified": datetime.fromtimestamp(entry.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            })
    return jsonify({"success": True, "files": files})


@app.route("/files/download/<file_type>/<path:filename>")
def download_file(file_type, filename):
    if file_type == "excel":
        folder = EXCEL_DIR
    elif file_type == "pdf":
        folder = PDF_DIR
    else:
        return jsonify({"success": False, "message": "Tipo de archivo inválido."}), 400
    return send_from_directory(folder, filename, as_attachment=True)


@app.route("/files/open/<file_type>/<path:filename>")
def open_file(file_type, filename):
    if file_type == "excel":
        folder = EXCEL_DIR
    elif file_type == "pdf":
        folder = PDF_DIR
    else:
        return jsonify({"success": False, "message": "Tipo de archivo inválido."}), 400
    return send_from_directory(folder, filename, as_attachment=False)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("DEBUG", "false").lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
