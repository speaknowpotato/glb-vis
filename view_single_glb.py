import os
from http.server import SimpleHTTPRequestHandler, HTTPServer


# <script src="https://cdn.jsdelivr.net/npm/three@0.146.0/build/three.min.js"></script>
# <script src="https://cdn.jsdelivr.net/npm/three@0.146.0/examples/js/loaders/GLTFLoader.js"></script>


# HTML content with Three.js to render the GLB file
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>View GLB Model</title>
    <style>
        body {{ margin: 0; overflow: hidden; }}
        canvas {{ display: block; }}
    </style>
</head>
<body>
    <script src="https://cdn.jsdelivr.net/npm/three@0.146.0/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.146.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.146.0/examples/js/loaders/GLTFLoader.js"></script>
    <script>
        // Create a scene, camera, and renderer
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // Add OrbitControls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true; // Enable smooth motion
        controls.dampingFactor = 0.05;

        // Load the GLB file
        const loader = new THREE.GLTFLoader();
        loader.load(
            "model1.glb", 
            function (gltf) {
                scene.add(gltf.scene);
                camera.position.z = 5;
                controls.update(); // Ensure controls are updated after model is loaded
            },
            undefined,
            function (error) {
                console.error('An error occurred loading the GLB file:', error);
            }
        );

        // Animation loop
        function animate() {
            requestAnimationFrame(animate);
            controls.update(); // Update controls in the animation loop
            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>
"""

# Write the HTML content to a file
html_file = "index.html"
with open(html_file, "w") as f:
    f.write(html_content)

# Serve the directory
print(f"Serving GLB viewer at http://localhost:8000/{html_file}")
os.chdir(".")
server_address = ("", 8000)
httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
httpd.serve_forever()
