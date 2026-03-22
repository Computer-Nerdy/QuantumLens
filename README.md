# QuantumLens
# 🛸 QuantumLens v4.0: Neural Interface Lab

![License](https://img.shields.io/badge/license-MIT-gold)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Qiskit](https://img.shields.io/badge/engine-Qiskit-purple)

**QuantumLens** is a high-fidelity, interactive quantum circuit simulator designed to bridge the gap between abstract linear algebra and visual intuition. Built with a "Cyberpunk Research Lab" aesthetic, it allows users to manipulate qubits in real-time and witness the immediate collapse of the wavefunction.

---

## 🌌 Key Features

### 1. **Wavefunction Field**
A dynamic, auto-animating probability distribution chart. Watch the amplitudes shift in real-time as you apply Hadamard, X, or Z gates. The CSS-driven "Dramatic Crawl" animation mimics the instability of a real quantum core.

### 2. **3D Holographic Console**
Powered by **Three.js**, this console renders multiple Bloch Spheres in a side-scrolling interface. 
* **Real-time Vector Tracking:** The state vector pulses based on the magnitude of the probability.
* **Partial Trace Integration:** Uses density matrix mathematics to visualize individual qubit states within an entangled system.

### 3. **Telemetry HUD**
A data-heavy dashboard showing the raw complex coefficients ($\psi = \alpha|0\rangle + \beta|1\rangle$) and percentage-based state probabilities.

### 4. **Advanced Research Mode**
Toggle for custom CX-Gate routing and continuous RY-Rotations ($\theta \pi$) for precise state preparation.

---

## 🛠️ Technical Stack

* **Logic Engine:** [Qiskit](https://qiskit.org/) (IBM Quantum)
* **Frontend:** [Streamlit](https://streamlit.io/)
* **3D Rendering:** [Three.js](https://threejs.org/) & Plotly
* **Styling:** Custom CSS Injectors with Base64 Asset Encoding (Offline Ready)

---

## 🚀 Installation & Local Deployment

This lab is designed to run entirely **offline** once the assets are loaded.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/QuantumLens-v4.git](https://github.com/YOUR_USERNAME/QuantumLens-v4.git)
   cd QuantumLens-v4
   ```
2. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Prepare Assets:
    Ensure the following files are in the /assets directory for the UI to render correctly:

        orbitron.ttf (Headers)

        jetbrains.ttf (Monospace Data)

        three.min.js (3D Engine)

        bg.jpg (Lab Background)

5. Launch the Interface:
   ```bash
   streamlit run app.py
   ```
# 🧬 Quantum Concepts Visualized:
        Superposition:
                Visualized via the H-Gate amplitude split. Witness a single state diverge into a 50/50 probability distribution.
        Entanglement:
                Demonstrated through Bell State generation ($|00\rangle + |11\rangle$). Link the fates of two qubits across the terminal.
        Collapse:
                Experience the "Observer Effect" by triggering the Measure protocol, which forces a non-reversible state selection and resets the system to a basis state.

#👤  **Author:**
            **HARISH RAGAV V** 
            (Lead Quantum Systems Architect)

"The universe is not only queerer than we suppose, but queerer than we can suppose." — J.B.S. Haldane
