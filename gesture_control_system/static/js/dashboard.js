// Dashboard Client Controller
document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const cameraStatusText = document.querySelector("#camera-status .badge-text");
    const cameraStatusIndicator = document.querySelector("#camera-status .status-indicator");
    const controlStatusText = document.querySelector("#control-status .badge-text");
    const controlStatusIndicator = document.querySelector("#control-status .status-indicator");
    
    const currGestureVal = document.getElementById("curr-gesture");
    const currConfidenceVal = document.getElementById("curr-confidence");
    const handLabelVal = document.getElementById("hand-label");
    const rawCoordsVal = document.getElementById("raw-coords");
    const smoothCoordsVal = document.getElementById("smooth-coords");
    
    const toggleOsControl = document.getElementById("toggle-os-control");
    const sensitivitySlider = document.getElementById("sensitivity-slider");
    const sensitivityValText = document.getElementById("sensitivity-val");
    const btnClearLogs = document.getElementById("btn-clear-logs");
    const consoleLogsContainer = document.getElementById("console-logs-container");
    
    // Robot SVG Elements
    const robotSvg = document.getElementById("robot-svg");
    const link1 = document.getElementById("link1");
    const link2 = document.getElementById("link2");
    const jointElbow = document.getElementById("joint-elbow");
    const jointWrist = document.getElementById("joint-wrist");
    const targetReticle = document.getElementById("target-reticle");
    const clawAssembly = document.getElementById("claw-assembly");
    const clawFingerL = document.getElementById("claw-finger-l");
    const clawFingerR = document.getElementById("claw-finger-r");
    
    // Telemetry labels
    const clawStateLabel = document.getElementById("claw-state-label");
    const simTargetLabel = document.getElementById("sim-target-label");
    const shoulderAngLabel = document.getElementById("shoulder-ang-label");
    const elbowAngLabel = document.getElementById("elbow-ang-label");
    
    // Application States
    let lastGesture = "None";
    let isCameraConnected = false;
    let isControlEnabled = false;
    
    // Robotic Arm Geometry
    const BASE_X = 200;
    const BASE_Y = 350;
    const L1 = 125; // Length of Link 1
    const L2 = 105; // Length of Link 2
    
    // SVG Claw Path Definitions (Open vs Closed)
    const CLAW_PATHS = {
        open: {
            l: "M -10 -5 C -25 -15 -22 -32 -5 -38 C -9 -25 -10 -15 -5 -5",
            r: "M 10 -5 C 25 -15 22 -32 5 -38 C 9 -25 10 -15 5 -5"
        },
        closed: {
            l: "M -10 -5 C -15 -18 -10 -30 -1 -35 C -3 -22 -6 -13 -5 -5",
            r: "M 10 -5 C 15 -18 10 -30 1 -35 C 3 -22 6 -13 5 -5"
        }
    };

    // 1. Initialize Status and Settings
    fetch("/api/status")
        .then(res => res.json())
        .then(data => {
            updateStatusUI(data.camera_connected, data.system_control_enabled);
            toggleOsControl.checked = data.system_control_enabled;
            logToConsole(`[SYSTEM] Backend report - Webcam connected: ${data.camera_connected}, OS Control active: ${data.system_control_enabled}`, "info");
        })
        .catch(err => {
            logToConsole(`[ERROR] Failed to query system status: ${err}`, "error");
        });

    // 2. Setup Event Listeners
    toggleOsControl.addEventListener("change", sendSettingsUpdate);
    sensitivitySlider.addEventListener("input", () => {
        sensitivityValText.innerText = `${sensitivitySlider.value}%`;
    });
    sensitivitySlider.addEventListener("change", sendSettingsUpdate);
    btnClearLogs.addEventListener("click", () => {
        consoleLogsContainer.innerHTML = "";
        logToConsole("[CONSOLE] History logs cleared.", "info");
    });

    // 3. Post Settings Helper
    function sendSettingsUpdate() {
        const payload = {
            enabled: toggleOsControl.checked,
            sensitivity: parseFloat(sensitivitySlider.value) / 100.0
        };
        
        fetch("/api/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            updateStatusUI(isCameraConnected, data.system_control_enabled);
            logToConsole(`[SETTING] OS control state saved to backend: ${data.system_control_enabled} (Sensitivity: ${Math.round(data.sensitivity * 100)}%)`, "info");
        })
        .catch(err => {
            logToConsole(`[ERROR] Failed to upload configuration settings: ${err}`, "error");
        });
    }

    // 4. Update UI Header Status Indicators
    function updateStatusUI(cameraConnected, controlEnabled) {
        isCameraConnected = cameraConnected;
        isControlEnabled = controlEnabled;
        
        // Webcam Indicator
        if (cameraConnected) {
            cameraStatusIndicator.className = "status-indicator green";
            cameraStatusText.innerText = "Camera: ONLINE";
        } else {
            cameraStatusIndicator.className = "status-indicator yellow";
            cameraStatusText.innerText = "Camera: SIMULATED (Demo)";
        }
        
        // Cursor Control Indicator
        if (controlEnabled) {
            controlStatusIndicator.className = "status-indicator green";
            controlStatusText.innerText = "OS Control: ACTIVE";
        } else {
            controlStatusIndicator.className = "status-indicator red";
            controlStatusText.innerText = "OS Control: OFF";
        }
    }

    // 5. Connect to SSE Telemetry Data Stream
    const dataStream = new EventSource("/data_stream");
    
    dataStream.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateTelemetryUI(data);
        driveRoboticArmSim(data.pointer_smoothed, data.gesture);
    };

    dataStream.onerror = (err) => {
        logToConsole("[ERROR] SSE Coordinate Stream disconnected or encountered error.", "error");
    };

    // 6. Update Telemetry Panels
    function updateTelemetryUI(data) {
        // UI text updates
        currGestureVal.innerText = data.gesture;
        currConfidenceVal.innerText = `${Math.round(data.confidence * 100)}%`;
        handLabelVal.innerText = data.label;
        rawCoordsVal.innerText = `${data.pointer_raw[0].toFixed(2)}, ${data.pointer_raw[1].toFixed(2)}`;
        smoothCoordsVal.innerText = `${data.pointer_smoothed[0].toFixed(2)}, ${data.pointer_smoothed[1].toFixed(2)}`;
        
        // Toggle camera simulation indicator if backend changes
        if (data.simulated && cameraStatusText.innerText.includes("ONLINE")) {
            updateStatusUI(false, isControlEnabled);
        } else if (!data.simulated && cameraStatusText.innerText.includes("SIMULATED")) {
            updateStatusUI(true, isControlEnabled);
        }
        
        // Handle log records when a gesture transition occurs
        if (data.gesture !== lastGesture) {
            if (data.gesture !== "None") {
                logToConsole(`[GESTURE] Detected: ${data.gesture} (${data.label} Hand)`, "info");
                
                // Active mapping highlighting in CSS table
                highlightMappingTableRow(data.gesture);
            } else {
                highlightMappingTableRow(null);
            }
            
            lastGesture = data.gesture;
        }
        
        // Log OS actions if triggered
        if (data.action !== "None" && data.action !== "Demo Coordinates Sent") {
            logToConsole(`[CONTROL] OS Triggered: ${data.action}`, "action");
        }
    }

    // Highlight row matching current gesture
    function highlightMappingTableRow(gesture) {
        // Remove active class from all rows
        document.querySelectorAll(".mapping-table tbody tr").forEach(row => {
            row.classList.remove("active-mapping");
            const badge = row.querySelector(".badge");
            if (badge) badge.classList.remove("active");
        });
        
        if (!gesture) return;
        
        // Match table row by ID suffix (e.g. row-Thumbs-Up)
        const rowId = `row-${gesture.replace(" ", "-")}`;
        const targetRow = document.getElementById(rowId);
        if (targetRow) {
            targetRow.classList.add("active-mapping");
            const badge = targetRow.querySelector(".badge");
            if (badge) badge.classList.add("active");
        }
    }

    // 7. Write to Log Console
    function logToConsole(message, type = "info") {
        const timeStr = new Date().toTimeString().split(' ')[0];
        const line = document.createElement("div");
        line.className = `console-line line-${type}`;
        line.innerText = `[${timeStr}] ${message}`;
        
        consoleLogsContainer.appendChild(line);
        
        // Limit console log size to 100 rows to prevent memory leakage
        while (consoleLogsContainer.childElementCount > 100) {
            consoleLogsContainer.removeChild(consoleLogsContainer.firstChild);
        }
        
        // Auto-scroll to bottom
        consoleLogsContainer.scrollTop = consoleLogsContainer.scrollHeight;
    }

    // 8. 2D Robotic Arm Sim Inverse Kinematics (IK) Solver
    function driveRoboticArmSim(pointerCoords, gesture) {
        // Target is relative inside the 400x400 SVG grid.
        // Screen X coordinates are mirrored, so flip X back for a matching direction
        const tx_norm = 1.0 - pointerCoords[0];
        const ty_norm = pointerCoords[1];
        
        // Limit coordinates to screen zone mapping
        // We map X from [0.1, 0.9] to [60, 340]
        // We map Y from [0.1, 0.9] to [60, 280]
        let tx = 60 + (tx_norm - 0.1) * (280 / 0.8);
        let ty = 60 + (ty_norm - 0.1) * (220 / 0.8);
        
        // Bound checks
        tx = Math.max(50, Math.min(350, tx));
        ty = Math.max(50, Math.min(320, ty));
        
        // Vector from Base to Target
        let dx = tx - BASE_X;
        let dy = ty - BASE_Y;
        let D = Math.sqrt(dx * dx + dy * dy);
        
        // Max distance is the sum of link lengths (with minor tolerance margin)
        const maxReach = L1 + L2 - 3;
        const minReach = 40;
        
        if (D > maxReach) {
            // Target is out of reach, project to reach boundary
            tx = BASE_X + (dx / D) * maxReach;
            ty = BASE_Y + (dy / D) * maxReach;
            dx = tx - BASE_X;
            dy = ty - BASE_Y;
            D = maxReach;
        } else if (D < minReach) {
            // Target is too close, push out slightly to avoid joint locking
            tx = BASE_X + (dx / D) * minReach;
            ty = BASE_Y + (dy / D) * minReach;
            dx = tx - BASE_X;
            dy = ty - BASE_Y;
            D = minReach;
        }
        
        // Inverse Kinematics calculations (Law of Cosines)
        // Cosine of angle at Elbow
        const cosElbow = (D * D - L1 * L1 - L2 * L2) / (2 * L1 * L2);
        // Compute Elbow Angle (radians)
        const elbowAngle = Math.acos(Math.max(-1.0, Math.min(1.0, cosElbow)));
        
        // Angle from base base to target
        const alpha = Math.atan2(dy, dx);
        
        // Angle offset for shoulder
        const cosShoulder = (L1 * L1 + D * D - L2 * L2) / (2 * L1 * D);
        const beta = Math.acos(Math.max(-1.0, Math.min(1.0, cosShoulder)));
        
        // Shoulder Angle (radians)
        const shoulderAngle = alpha - beta;
        
        // Compute intermediate Joint: Elbow Coordinate
        const ex = BASE_X + L1 * Math.cos(shoulderAngle);
        const ey = BASE_Y + L1 * Math.sin(shoulderAngle);
        
        // Compute End Effector: Wrist coordinate is at target (tx, ty)
        const wx = tx;
        const wy = ty;
        
        // Update SVG line segments and nodes
        link1.setAttribute("x1", BASE_X);
        link1.setAttribute("y1", BASE_Y);
        link1.setAttribute("x2", ex);
        link1.setAttribute("y2", ey);
        
        link2.setAttribute("x1", ex);
        link2.setAttribute("y1", ey);
        link2.setAttribute("x2", wx);
        link2.setAttribute("y2", wy);
        
        jointElbow.setAttribute("cx", ex);
        jointElbow.setAttribute("cy", ey);
        
        jointWrist.setAttribute("cx", wx);
        jointWrist.setAttribute("cy", wy);
        
        // Render target marker
        targetReticle.setAttribute("transform", `translate(${wx - 200}, ${wy - 200})`);
        
        // Rotate and position claw assembly at the wrist
        // Angle of Link 2 determines the orientation of claw
        const link2Angle = Math.atan2(wy - ey, wx - ex);
        const clawAngleDeg = (link2Angle * 180 / Math.PI) + 90; // Add offset to orient upward
        
        clawAssembly.setAttribute("transform", `translate(${wx}, ${wy}) rotate(${clawAngleDeg})`);
        
        // Toggle Claw gripper path according to gesture
        const isClawClosed = (gesture === "Fist" || gesture === "Pinch");
        if (isClawClosed) {
            clawFingerL.setAttribute("d", CLAW_PATHS.closed.l);
            clawFingerR.setAttribute("d", CLAW_PATHS.closed.r);
            clawStateLabel.innerText = "CLOSED";
            clawStateLabel.className = "text-glow-red";
        } else {
            clawFingerL.setAttribute("d", CLAW_PATHS.open.l);
            clawFingerR.setAttribute("d", CLAW_PATHS.open.r);
            clawStateLabel.innerText = "OPEN";
            clawStateLabel.className = "text-glow-green";
        }
        
        // Update dashboard labels
        simTargetLabel.innerText = `${Math.round(wx)}, ${Math.round(wy)}`;
        // Convert to human readable angles: standard references
        const shAngDeg = Math.round((-shoulderAngle * 180 / Math.PI));
        const elAngDeg = Math.round((elbowAngle * 180 / Math.PI));
        shoulderAngLabel.innerText = `${shAngDeg}°`;
        elbowAngLabel.innerText = `${elAngDeg}°`;
    }
});
