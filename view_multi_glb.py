import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Define the maximum number of models to display
MAX_MODELS = 4

# Define default GLB files (optional)
default_glbs = []  # Set to empty list [] if no default models

# Generate viewport divs dynamically based on MAX_MODELS
viewport_divs = "\n            ".join(
    [
        f"""
                <div id="viewport{i+1}" class="viewport">
                    <div class="loader" id="loader{i+1}">Loading Model {i+1}...</div>
                </div>"""
        for i in range(MAX_MODELS)
    ]
)

# Prepare scripts to load default models if any
load_default_scripts = (
    "\n            ".join(
        [
            f"loadModel({i}, '{default_glbs[i]}');"
            for i in range(min(len(default_glbs), MAX_MODELS))
        ]
    )
    if default_glbs
    else ""
)

# HTML content with Three.js to render up to four GLB files based on search input
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GLB Model Viewer with Multi-Search</title>
    <style>
        body {{
            margin: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
            font-family: Arial, sans-serif;
        }}
        #search-bar {{
            padding: 10px;
            background-color: #f0f0f0;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
        }}
        #search-input {{
            flex: 1;
            padding: 8px;
            font-size: 1em;
            border: 1px solid #ccc;
            border-radius: 4px;
            min-width: 200px;
        }}
        #search-button {{
            padding: 8px 16px;
            margin-left: 10px;
            font-size: 1em;
            border: none;
            border-radius: 4px;
            background-color: #007BFF;
            color: white;
            cursor: pointer;
            margin-top: 5px;
        }}
        #search-button:hover {{
            background-color: #0056b3;
        }}
        #reset-button {{
            padding: 8px 16px;
            margin-left: 10px;
            font-size: 1em;
            border: none;
            border-radius: 4px;
            background-color: #dc3545;
            color: white;
            cursor: pointer;
            margin-top: 5px;
        }}
        #reset-button:hover {{
            background-color: #c82333;
        }}
        #error-message {{
            color: red;
            margin-left: 10px;
            margin-top: 5px;
            flex-basis: 100%;
        }}
        #viewports {{
            flex: 1;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 1px;
            background-color: #ccc;
            height: calc(100vh - 60px); /* Adjust based on search bar height */
        }}
        .viewport {{
            position: relative;
            background-color: #fff;
        }}
        canvas {{
            width: 100%;
            height: 100%;
            display: block;
        }}
        .loader {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.2em;
            color: #555;
            display: none; /* Hidden by default */
        }}
    </style>
</head>
<body>
    <div id="search-bar">
        <input type="text" id="search-input" placeholder="Enter GLB filenames (e.g., model1.glb, model2.glb)">
        <button id="search-button">Load Models</button>
        <button id="reset-button">Reset All Models</button>
        <div id="error-message"></div>
    </div>
    <div id="viewports">
        {viewport_divs}
    </div>

    <!-- Three.js and necessary scripts -->
    <script src="https://cdn.jsdelivr.net/npm/three@0.146.0/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.146.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.146.0/examples/js/loaders/GLTFLoader.js"></script>

    <script>
        // Maximum number of models
        const MAX_MODELS = {max_models};

        // Initialize variables
        let scenes = [];
        let cameras = [];
        let renderers = [];
        let controlsList = [];
        let loaders = [];

        // Initialize the Three.js scenes for each viewport
        function initScenes() {{
            for(let i = 0; i < MAX_MODELS; i++) {{
                const containerId = 'viewport' + (i+1);
                const loaderId = 'loader' + (i+1);

                // Get container element
                const container = document.getElementById(containerId);

                // Create scene
                const scene = new THREE.Scene();
                scenes.push(scene);

                // Create camera
                const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
                camera.position.z = 5;
                cameras.push(camera);

                // Create renderer
                const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                renderer.setSize(container.clientWidth, container.clientHeight);
                container.appendChild(renderer.domElement);
                renderers.push(renderer);

                // Create OrbitControls
                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                controlsList.push(controls);

                // Add ambient light
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
                scene.add(ambientLight);

                // Add directional light
                const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                directionalLight.position.set(1, 1, 1).normalize();
                scene.add(directionalLight);

                // Initialize GLTFLoader
                const loader = new THREE.GLTFLoader();
                loaders.push(loader);
            }}

            window.addEventListener('resize', onWindowResize, false);
            animate();
        }}

        // Handle window resize
        function onWindowResize() {{
            for(let i = 0; i < MAX_MODELS; i++) {{
                const containerId = 'viewport' + (i+1);
                const container = document.getElementById(containerId);
                const renderer = renderers[i];
                const camera = cameras[i];

                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }}
        }}

        // Animation loop
        function animate() {{
            requestAnimationFrame(animate);
            for(let i = 0; i < MAX_MODELS; i++) {{
                controlsList[i].update();
                renderers[i].render(scenes[i], cameras[i]);
            }}
        }}

        // Function to load a GLB model into a specific viewport
        function loadModel(index, filename) {{
            const scene = scenes[index];
            const loader = loaders[index];
            const loaderId = 'loader' + (index+1);

            // Clear previous scene objects except lights
            scene.traverse(function(child) {{
                if(child.isMesh || child.isGroup) {{
                    scene.remove(child);
                }}
            }});

            // Show loader
            document.getElementById(loaderId).style.display = 'block';

            loader.load(
                filename,
                function(gltf) {{
                    scene.add(gltf.scene);
                    adjustCamera(index, gltf.scene);
                    // Hide loader
                    document.getElementById(loaderId).style.display = 'none';
                }},
                undefined,
                function(error) {{
                    console.error('An error occurred loading the GLB file:', error);
                    document.getElementById(loaderId).style.display = 'none';
                    alert('Failed to load model: ' + filename + ' in viewport ' + (index+1));
                }}
            );
        }}

        // Function to adjust camera to fit the model
        function adjustCamera(index, model) {{
            const camera = cameras[index];
            const controls = controlsList[index];
            const scene = scenes[index];

            // Compute bounding box
            const box = new THREE.Box3().setFromObject(model);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());

            // Reposition the model to the origin
            model.position.x += (model.position.x - center.x);
            model.position.y += (model.position.y - center.y);
            model.position.z += (model.position.z - center.z);

            // Compute max dimension
            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = camera.fov * (Math.PI / 180);
            let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));

            cameraZ *= 1.5; // Zoom out a bit for better view

            camera.position.z = cameraZ;

            // Set controls target
            controls.target.set(center.x, center.y, center.z);
            controls.update();
        }}

        // Function to load multiple models based on input
        function loadModels(filenames) {{
            for(let i = 0; i < MAX_MODELS; i++) {{
                if(i < filenames.length) {{
                    loadModel(i, filenames[i]);
                }} else {{
                    // Clear viewport if no model specified
                    clearViewport(i);
                }}
            }}
        }}

        // Function to clear a viewport
        function clearViewport(index) {{
            const scene = scenes[index];
            const loaderId = 'loader' + (index+1);

            // Remove all objects except lights
            scene.traverse(function(child) {{
                if(child.isMesh || child.isGroup) {{
                    scene.remove(child);
                }}
            }});

            // Dispose geometries and materials
            scene.traverse(function(child) {{
                if(child.isMesh) {{
                    if(child.geometry) {{
                        child.geometry.dispose();
                    }}
                    if(child.material) {{
                        if(Array.isArray(child.material)) {{
                            child.material.forEach(material => disposeMaterial(material));
                        }} else {{
                            disposeMaterial(child.material);
                        }}
                    }}
                }}
            }});

            // Hide loader
            document.getElementById(loaderId).style.display = 'none';

            // Reset camera position
            cameras[index].position.z = 5;
            controlsList[index].target.set(0, 0, 0);
            controlsList[index].update();
        }}

        // Helper function to dispose of materials
        function disposeMaterial(material) {{
            material.dispose();
            // Dispose of textures if any
            for (const key in material) {{
                const value = material[key];
                if (value && typeof value === 'object' && 'minFilter' in value) {{
                    value.dispose();
                }}
            }}
        }}

        // Function to reset all viewports
        function resetAllViewports() {{
            for(let i = 0; i < MAX_MODELS; i++) {{
                clearViewport(i);
            }}
            // Clear search input and error message
            document.getElementById('search-input').value = '';
            document.getElementById('error-message').innerText = '';
        }}

        // Handle search button click
        document.getElementById('search-button').addEventListener('click', function() {{
            const input = document.getElementById('search-input').value.trim();
            if(input === '') {{
                document.getElementById('error-message').innerText = 'Please enter at least one filename.';
                return;
            }}

            // Split input by comma or space
            let filenames = input.split(/[,\\s]+/).filter(name => name.toLowerCase().endsWith('.glb'));
            if(filenames.length === 0) {{
                document.getElementById('error-message').innerText = 'Please enter valid GLB filenames ending with .glb';
                return;
            }}

            // Limit to MAX_MODELS
            if(filenames.length > MAX_MODELS) {{
                filenames = filenames.slice(0, MAX_MODELS);
                alert('Only the first {max_models} models will be loaded.');
            }}

            document.getElementById('error-message').innerText = '';

            loadModels(filenames);
        }});

        // Handle Reset button click
        document.getElementById('reset-button').addEventListener('click', function() {{
            resetAllViewports();
        }});

        // Handle Enter key in search input
        document.getElementById('search-input').addEventListener('keypress', function(event) {{
            if(event.key === 'Enter') {{
                document.getElementById('search-button').click();
            }}
        }});

        // Initialize the scenes on page load
        window.onload = function() {{
            initScenes();
            {load_default_scripts}
        }};
    </script>
</body>
</html>
""".format(
    viewport_divs=viewport_divs,
    max_models=MAX_MODELS,
    load_default_scripts=load_default_scripts,
)

# Write the HTML content to a file
html_file = "index.html"
with open(html_file, "w") as f:
    f.write(html_content)

# Serve the directory
print(
    f"Serving GLB viewer with {MAX_MODELS}-section support at http://localhost:8000/{html_file}"
)
os.chdir(".")
server_address = ("", 8000)
httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
try:
    print("HTTP server is running. Press Ctrl+C to stop.")
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nShutting down the server.")
    httpd.server_close()
