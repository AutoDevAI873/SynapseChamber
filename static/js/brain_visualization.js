/**
 * Synapse Chamber 3D Brain Visualization
 * 
 * A realistic 3D brain visualization that shows the neural activity
 * and connections between different components of the system.
 */

// Import dependencies
// Note: In production, you'd use proper imports, but for simplicity with script tags:
// const THREE = window.THREE;

class BrainVisualization {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with ID "${containerId}" not found`);
            return;
        }

        // Configuration
        this.options = Object.assign({
            backgroundColor: 0x000000,
            brainColor: 0x888888,
            activeNeuronColor: 0x00ffff,
            synapseColor: 0x0088ff,
            rotationSpeed: 0.001,
            neuronCount: 300,
            synapseCount: 500,
            pulseDuration: 2000, // ms
            showLabels: true,
            enableInteraction: true,
            healthBarId: 'brainHealthBar'
        }, options);

        // System components mapping
        this.systemMapping = {
            'brainstem': { name: 'Brainstem', component: 'main.py', position: [0, -50, 0], scale: 1.2 },
            'frontal_lobe': { name: 'Frontal Lobe', component: 'self_training_system.py', position: [0, 60, 40], scale: 1.4 },
            'temporal_lobe': { name: 'Temporal Lobe', component: 'ai_controller.py', position: [60, 0, 0], scale: 1.3 },
            'parietal_lobe': { name: 'Parietal Lobe', component: 'training_engine.py', position: [0, 50, -40], scale: 1.2 },
            'occipital_lobe': { name: 'Occipital Lobe', component: 'browser_automation.py', position: [-60, -30, -30], scale: 1.1 },
            'cerebellum': { name: 'Cerebellum', component: 'agent_system.py', position: [0, -60, -30], scale: 1.0 },
            'hippocampus': { name: 'Hippocampus', component: 'memory_system.py', position: [30, -20, 20], scale: 0.8 },
            'amygdala': { name: 'Amygdala', component: 'analytics_system.py', position: [-30, -20, 20], scale: 0.7 },
            'thalamus': { name: 'Thalamus', component: 'recommendation_engine.py', position: [0, 0, 0], scale: 0.6 },
            'hypothalamus': { name: 'Hypothalamus', component: 'gamification_system.py', position: [0, -10, 10], scale: 0.6 }
        };

        // Active neurons tracking
        this.activeNeurons = new Set();
        this.neurons = [];
        this.synapses = [];
        this.brainRegions = {};
        this.componentActivity = {};
        
        // Initialize health metrics
        this.healthMetrics = {
            overall: 100,
            memory: 100,
            training: 100,
            apiConnections: 100,
            lastUpdate: Date.now()
        };

        // Setup the visualization
        this.initScene();
        this.initCamera();
        this.initRenderer();
        this.initControls();
        this.initLights();
        this.createBrain();
        this.initEventListeners();
        this.initWebSocket();
        this.updateHealthBar();
        
        // Start animation loop
        this.animate();
    }

    initScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(this.options.backgroundColor);
        this.scene.fog = new THREE.FogExp2(this.options.backgroundColor, 0.001);
    }

    initCamera() {
        const containerRect = this.container.getBoundingClientRect();
        const width = containerRect.width;
        const height = containerRect.height;
        
        this.camera = new THREE.PerspectiveCamera(60, width / height, 1, 2000);
        this.camera.position.set(0, 0, 300);
        this.camera.lookAt(0, 0, 0);
    }

    initRenderer() {
        const containerRect = this.container.getBoundingClientRect();
        const width = containerRect.width;
        const height = containerRect.height;
        
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.setSize(width, height);
        this.renderer.outputEncoding = THREE.sRGBEncoding;
        
        this.container.appendChild(this.renderer.domElement);
    }

    initControls() {
        if (this.options.enableInteraction && typeof THREE.OrbitControls !== 'undefined') {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.05;
            this.controls.screenSpacePanning = false;
            this.controls.minDistance = 100;
            this.controls.maxDistance = 500;
            this.controls.maxPolarAngle = Math.PI;
            this.controls.autoRotate = true;
            this.controls.autoRotateSpeed = 0.5;
        }
    }

    initLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040);
        this.scene.add(ambientLight);
        
        // Directional light (sun-like)
        const dirLight = new THREE.DirectionalLight(0xffffff, 1);
        dirLight.position.set(1, 1, 1);
        this.scene.add(dirLight);
        
        // Point lights for dramatic effect
        const pointLight1 = new THREE.PointLight(0x0088ff, 1, 150);
        pointLight1.position.set(50, 50, 50);
        this.scene.add(pointLight1);
        
        const pointLight2 = new THREE.PointLight(0xff8800, 1, 150);
        pointLight2.position.set(-50, -50, -50);
        this.scene.add(pointLight2);
    }

    createBrain() {
        // Create main brain geometry (semi-transparent)
        const brainGeometry = new THREE.SphereGeometry(90, 32, 32);
        const brainMaterial = new THREE.MeshPhongMaterial({
            color: this.options.brainColor,
            transparent: true,
            opacity: 0.1,
            wireframe: true
        });
        
        this.brainMesh = new THREE.Mesh(brainGeometry, brainMaterial);
        this.scene.add(this.brainMesh);
        
        // Create brain regions
        this.createBrainRegions();
        
        // Create neurons
        this.createNeurons();
        
        // Create synapses
        this.createSynapses();
        
        // Add text labels if enabled
        if (this.options.showLabels) {
            this.addLabels();
        }
    }

    createBrainRegions() {
        const regionGroup = new THREE.Group();
        this.scene.add(regionGroup);
        
        // Create a region for each mapped component
        Object.entries(this.systemMapping).forEach(([key, data]) => {
            // Create region geometry
            const geometry = new THREE.SphereGeometry(10 * data.scale, 16, 16);
            const material = new THREE.MeshPhongMaterial({
                color: this.getRandomColor(),
                transparent: true,
                opacity: 0.5
            });
            
            const region = new THREE.Mesh(geometry, material);
            region.position.set(...data.position);
            
            // Store the region
            this.brainRegions[key] = {
                mesh: region,
                data: data,
                initialColor: material.color.clone(),
                isActive: false
            };
            
            // Add to scene
            regionGroup.add(region);
        });
    }

    createNeurons() {
        // Create neuron geometry (small spheres)
        const neuronGeometry = new THREE.SphereGeometry(0.8, 8, 8);
        const neuronMaterial = new THREE.MeshPhongMaterial({
            color: 0xaaaaaa,
            emissive: 0x333333
        });
        
        // Create neuron group
        const neuronGroup = new THREE.Group();
        this.scene.add(neuronGroup);
        
        // Generate random neurons within brain volume
        for (let i = 0; i < this.options.neuronCount; i++) {
            const neuron = new THREE.Mesh(neuronGeometry, neuronMaterial.clone());
            
            // Random position within brain sphere
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(2 * Math.random() - 1);
            const radius = 40 + Math.random() * 45; // Between 40 and 85
            
            neuron.position.x = radius * Math.sin(phi) * Math.cos(theta);
            neuron.position.y = radius * Math.sin(phi) * Math.sin(theta);
            neuron.position.z = radius * Math.cos(phi);
            
            // Store reference
            this.neurons.push({
                mesh: neuron,
                isActive: false,
                activationTime: 0,
                material: neuron.material
            });
            
            neuronGroup.add(neuron);
        }
    }

    createSynapses() {
        // Create synapse material (lines)
        const synapseMaterial = new THREE.LineBasicMaterial({
            color: this.options.synapseColor,
            transparent: true,
            opacity: 0.2,
            linewidth: 1
        });
        
        // Create synapse group
        const synapseGroup = new THREE.Group();
        this.scene.add(synapseGroup);
        
        // Create random connections between neurons
        for (let i = 0; i < this.options.synapseCount; i++) {
            // Select two random neurons to connect
            const neuron1 = this.neurons[Math.floor(Math.random() * this.neurons.length)];
            const neuron2 = this.neurons[Math.floor(Math.random() * this.neurons.length)];
            
            // Don't connect a neuron to itself
            if (neuron1 === neuron2) continue;
            
            // Create geometry for this synapse
            const points = [
                neuron1.mesh.position.clone(),
                neuron2.mesh.position.clone()
            ];
            
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const line = new THREE.Line(geometry, synapseMaterial.clone());
            
            // Store reference
            this.synapses.push({
                line: line,
                neuron1: neuron1,
                neuron2: neuron2,
                isActive: false,
                activationTime: 0,
                material: line.material
            });
            
            synapseGroup.add(line);
        }
    }

    addLabels() {
        // Create a group for all labels
        const labelGroup = new THREE.Group();
        this.scene.add(labelGroup);
        
        // Add label for each region
        Object.entries(this.brainRegions).forEach(([key, region]) => {
            const data = region.data;
            
            // Create DOM element for label
            const labelDiv = document.createElement('div');
            labelDiv.className = 'brain-region-label';
            labelDiv.textContent = `${data.name} (${data.component})`;
            labelDiv.style.position = 'absolute';
            labelDiv.style.color = '#ffffff';
            labelDiv.style.padding = '4px';
            labelDiv.style.borderRadius = '2px';
            labelDiv.style.fontSize = '10px';
            labelDiv.style.backgroundColor = 'rgba(0,0,0,0.5)';
            labelDiv.style.pointerEvents = 'none';
            labelDiv.style.display = 'none'; // Initially hidden
            
            this.container.appendChild(labelDiv);
            
            // Store the label for updating
            region.label = labelDiv;
        });
    }

    updateLabels() {
        if (!this.options.showLabels) return;
        
        Object.values(this.brainRegions).forEach(region => {
            if (!region.label) return;
            
            // Convert 3D position to screen position
            const position = region.mesh.position.clone();
            position.project(this.camera);
            
            // Convert normalized position to container coordinates
            const rect = this.container.getBoundingClientRect();
            const x = (position.x * 0.5 + 0.5) * rect.width;
            const y = (-position.y * 0.5 + 0.5) * rect.height;
            
            // Check if region is in front of the camera (z < 1)
            if (position.z < 1) {
                region.label.style.display = 'block';
                region.label.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px)`;
                
                // Fade based on distance from camera center
                const distance = Math.sqrt(position.x ** 2 + position.y ** 2);
                const opacity = 1.0 - Math.min(distance * 1.2, 0.9);
                region.label.style.opacity = opacity.toString();
            } else {
                region.label.style.display = 'none';
            }
        });
    }

    // Add neurons that follow specific paths between regions
    addPathedNeurons() {
        // Define some common paths between regions
        const paths = [
            // From brainstem to frontal lobe (control flow)
            ['brainstem', 'frontal_lobe'],
            // Memory system connections
            ['hippocampus', 'frontal_lobe'],
            ['hippocampus', 'thalamus'],
            // Training flow
            ['frontal_lobe', 'temporal_lobe'],
            ['temporal_lobe', 'parietal_lobe'],
            ['parietal_lobe', 'cerebellum'],
            // Analytics
            ['cerebellum', 'amygdala'],
            ['amygdala', 'hypothalamus'],
            // Recommendation
            ['thalamus', 'frontal_lobe'],
            ['thalamus', 'hypothalamus']
        ];
        
        // Create pathed neurons
        paths.forEach(path => {
            const sourceRegion = this.brainRegions[path[0]];
            const targetRegion = this.brainRegions[path[1]];
            
            if (!sourceRegion || !targetRegion) return;
            
            // Create a curve between the regions for neurons to follow
            const startPoint = sourceRegion.mesh.position.clone();
            const endPoint = targetRegion.mesh.position.clone();
            
            // Add some variation to the curve
            const midPoint = new THREE.Vector3().addVectors(startPoint, endPoint).multiplyScalar(0.5);
            midPoint.add(new THREE.Vector3(
                (Math.random() - 0.5) * 20,
                (Math.random() - 0.5) * 20,
                (Math.random() - 0.5) * 20
            ));
            
            // Create a quadratic bezier curve
            const curve = new THREE.QuadraticBezierCurve3(
                startPoint,
                midPoint,
                endPoint
            );
            
            // Store the path for signal propagation
            if (!this.neuronPaths) this.neuronPaths = [];
            this.neuronPaths.push({
                curve: curve,
                source: path[0],
                target: path[1],
                signals: [] // Will store active signals
            });
        });
    }

    // Activate a component and trigger neural activity
    activateComponent(componentName, intensity = 1.0) {
        // Find relevant brain region
        const region = Object.values(this.brainRegions).find(r => r.data.component === componentName);
        if (!region) return;
        
        const regionId = Object.keys(this.brainRegions).find(key => this.brainRegions[key] === region);
        if (!regionId) return;
        
        // Mark component as active
        this.componentActivity[componentName] = {
            lastActivation: Date.now(),
            intensity: intensity
        };
        
        // Highlight brain region
        region.isActive = true;
        region.activationTime = Date.now();
        
        // Update material
        region.mesh.material.color.set(0x00ffff);
        region.mesh.material.opacity = 0.8;
        region.mesh.material.emissive = new THREE.Color(0x0088ff);
        region.mesh.material.emissiveIntensity = 0.5;
        
        // Create pulse effect
        this.createPulseEffect(region.mesh.position.clone(), 10 * region.data.scale);
        
        // Activate nearby neurons
        this.activateNeuronsNearRegion(region);
        
        // Trigger signals along paths from this region
        if (this.neuronPaths) {
            this.neuronPaths.forEach(path => {
                if (path.source === regionId) {
                    this.triggerSignalAlongPath(path);
                }
            });
        }
        
        // Create electricity effect
        this.createElectricityEffect(region.mesh.position.clone());
    }

    // Create a pulse effect at a position
    createPulseEffect(position, radius) {
        const geometry = new THREE.SphereGeometry(radius, 32, 32);
        const material = new THREE.MeshBasicMaterial({
            color: 0x00ffff,
            transparent: true,
            opacity: 0.3,
            wireframe: true
        });
        
        const pulse = new THREE.Mesh(geometry, material);
        pulse.position.copy(position);
        pulse.scale.set(0.1, 0.1, 0.1);
        this.scene.add(pulse);
        
        // Store for animation
        if (!this.pulseEffects) this.pulseEffects = [];
        this.pulseEffects.push({
            mesh: pulse,
            startTime: Date.now(),
            duration: 1000,
            maxScale: 1.5
        });
    }

    // Create electricity effect between two points
    createElectricityEffect(startPosition, endPosition) {
        if (!endPosition) {
            // If no end position is provided, create a random endpoint nearby
            endPosition = startPosition.clone().add(
                new THREE.Vector3(
                    (Math.random() - 0.5) * 40,
                    (Math.random() - 0.5) * 40,
                    (Math.random() - 0.5) * 40
                )
            );
        }
        
        // Create lightning bolt points (jagged line)
        const points = [];
        const segments = 10;
        const startToEnd = endPosition.clone().sub(startPosition);
        const segmentLength = startToEnd.length() / segments;
        
        points.push(startPosition.clone());
        
        for (let i = 1; i < segments; i++) {
            const point = startPosition.clone().add(
                startToEnd.clone().multiplyScalar(i / segments)
            );
            
            // Add some randomness
            point.add(
                new THREE.Vector3(
                    (Math.random() - 0.5) * segmentLength * 0.5,
                    (Math.random() - 0.5) * segmentLength * 0.5,
                    (Math.random() - 0.5) * segmentLength * 0.5
                )
            );
            
            points.push(point);
        }
        
        points.push(endPosition.clone());
        
        // Create the lightning geometry
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        
        // Create glowing material
        const material = new THREE.LineBasicMaterial({
            color: 0x00ffff,
            transparent: true,
            opacity: 0.8
        });
        
        const lightning = new THREE.Line(geometry, material);
        this.scene.add(lightning);
        
        // Store for animation
        if (!this.electricityEffects) this.electricityEffects = [];
        this.electricityEffects.push({
            mesh: lightning,
            startTime: Date.now(),
            duration: 500
        });
    }

    // Activate neurons near a specific region
    activateNeuronsNearRegion(region) {
        const position = region.mesh.position;
        const radius = 30 * region.data.scale;
        
        // Activate neurons within radius
        this.neurons.forEach(neuron => {
            if (neuron.mesh.position.distanceTo(position) < radius) {
                if (Math.random() < 0.7) { // 70% chance to activate
                    this.activateNeuron(neuron);
                }
            }
        });
        
        // Activate synapses where both neurons are active
        this.synapses.forEach(synapse => {
            if (synapse.neuron1.isActive && synapse.neuron2.isActive) {
                this.activateSynapse(synapse);
            }
        });
    }

    // Activate a single neuron
    activateNeuron(neuron) {
        neuron.isActive = true;
        neuron.activationTime = Date.now();
        neuron.material.color.set(this.options.activeNeuronColor);
        neuron.material.emissive.set(this.options.activeNeuronColor);
        neuron.material.emissiveIntensity = 0.7;
        
        // Scale up slightly
        neuron.mesh.scale.set(1.5, 1.5, 1.5);
    }

    // Activate a synapse (connection between neurons)
    activateSynapse(synapse) {
        synapse.isActive = true;
        synapse.activationTime = Date.now();
        synapse.material.color.set(this.options.synapseColor);
        synapse.material.opacity = 0.8;
    }

    // Trigger a signal along a neural path
    triggerSignalAlongPath(path) {
        // Create a new signal with starting position of 0 (start of curve)
        const signal = {
            position: 0, // 0 to 1 along the curve
            speed: 0.001 * (Math.random() * 0.5 + 0.75), // Random speed variation
            startTime: Date.now()
        };
        
        path.signals.push(signal);
    }

    // Update component health metrics
    updateHealthMetrics() {
        // Simulate health changes based on system activity
        // In a real application, these would come from actual system metrics
        
        // Decay health slightly over time
        const now = Date.now();
        const timeDelta = now - this.healthMetrics.lastUpdate;
        
        // Add some random fluctuation
        const randomFluctuation = (Math.random() - 0.5) * 0.1 * timeDelta / 1000;
        
        // Update overall health
        this.healthMetrics.memory = Math.max(0, Math.min(100, 
            this.healthMetrics.memory - 0.01 * timeDelta / 1000 + randomFluctuation));
            
        this.healthMetrics.training = Math.max(0, Math.min(100, 
            this.healthMetrics.training - 0.02 * timeDelta / 1000 + randomFluctuation));
            
        this.healthMetrics.apiConnections = Math.max(0, Math.min(100, 
            this.healthMetrics.apiConnections - 0.015 * timeDelta / 1000 + randomFluctuation * 2));
        
        // Overall health is average of components
        this.healthMetrics.overall = (
            this.healthMetrics.memory + 
            this.healthMetrics.training + 
            this.healthMetrics.apiConnections
        ) / 3;
        
        // Boost health for active components
        Object.entries(this.componentActivity).forEach(([component, activity]) => {
            // Only consider recent activity (last 5 seconds)
            if (now - activity.lastActivation < 5000) {
                if (component.includes('memory')) {
                    this.healthMetrics.memory += 0.5 * activity.intensity;
                } else if (component.includes('training')) {
                    this.healthMetrics.training += 0.5 * activity.intensity;
                } else if (component.includes('controller') || component.includes('browser')) {
                    this.healthMetrics.apiConnections += 0.5 * activity.intensity;
                }
                
                // Cap at 100
                this.healthMetrics.memory = Math.min(100, this.healthMetrics.memory);
                this.healthMetrics.training = Math.min(100, this.healthMetrics.training);
                this.healthMetrics.apiConnections = Math.min(100, this.healthMetrics.apiConnections);
            }
        });
        
        this.healthMetrics.lastUpdate = now;
        
        // Update health bar
        this.updateHealthBar();
    }

    // Update health bar display
    updateHealthBar() {
        const healthBar = document.getElementById(this.options.healthBarId);
        if (!healthBar) return;
        
        // Update overall health
        const overallBar = healthBar.querySelector('.overall-health-bar');
        if (overallBar) {
            overallBar.style.width = `${this.healthMetrics.overall}%`;
            
            // Update color based on health
            if (this.healthMetrics.overall > 75) {
                overallBar.className = 'health-bar-inner overall-health-bar bg-success';
            } else if (this.healthMetrics.overall > 40) {
                overallBar.className = 'health-bar-inner overall-health-bar bg-warning';
            } else {
                overallBar.className = 'health-bar-inner overall-health-bar bg-danger';
            }
        }
        
        // Update component health metrics
        const memoryBar = healthBar.querySelector('.memory-health-bar');
        if (memoryBar) {
            memoryBar.style.width = `${this.healthMetrics.memory}%`;
        }
        
        const trainingBar = healthBar.querySelector('.training-health-bar');
        if (trainingBar) {
            trainingBar.style.width = `${this.healthMetrics.training}%`;
        }
        
        const apiBar = healthBar.querySelector('.api-health-bar');
        if (apiBar) {
            apiBar.style.width = `${this.healthMetrics.apiConnections}%`;
        }
    }

    // Handle animation updates
    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.updateScene();
        this.render();
        
        // Update controls if available
        if (this.controls) {
            this.controls.update();
        }
    }

    // Update all the visual elements
    updateScene() {
        const now = Date.now();
        
        // Rotate brain slightly
        this.brainMesh.rotation.y += this.options.rotationSpeed;
        
        // Update brain regions
        Object.values(this.brainRegions).forEach(region => {
            if (region.isActive) {
                const elapsed = now - region.activationTime;
                if (elapsed > this.options.pulseDuration) {
                    // Reset to inactive
                    region.isActive = false;
                    region.mesh.material.color.copy(region.initialColor);
                    region.mesh.material.opacity = 0.5;
                    region.mesh.material.emissiveIntensity = 0;
                } else {
                    // Pulse effect
                    const pulse = 1 - elapsed / this.options.pulseDuration;
                    region.mesh.material.opacity = 0.5 + 0.3 * pulse;
                    region.mesh.material.emissiveIntensity = 0.5 * pulse;
                }
            }
        });
        
        // Update active neurons
        this.neurons.forEach(neuron => {
            if (neuron.isActive) {
                const elapsed = now - neuron.activationTime;
                if (elapsed > this.options.pulseDuration) {
                    // Reset to inactive
                    neuron.isActive = false;
                    neuron.material.color.set(0xaaaaaa);
                    neuron.material.emissive.set(0x333333);
                    neuron.material.emissiveIntensity = 0.2;
                    neuron.mesh.scale.set(1, 1, 1);
                } else {
                    // Fade out effect
                    const fade = 1 - elapsed / this.options.pulseDuration;
                    neuron.material.emissiveIntensity = 0.7 * fade;
                    const scale = 1 + 0.5 * fade;
                    neuron.mesh.scale.set(scale, scale, scale);
                }
            }
        });
        
        // Update active synapses
        this.synapses.forEach(synapse => {
            if (synapse.isActive) {
                const elapsed = now - synapse.activationTime;
                if (elapsed > this.options.pulseDuration) {
                    // Reset to inactive
                    synapse.isActive = false;
                    synapse.material.opacity = 0.2;
                } else {
                    // Fade out effect
                    const fade = 1 - elapsed / this.options.pulseDuration;
                    synapse.material.opacity = 0.2 + 0.6 * fade;
                }
            }
        });
        
        // Update pulse effects
        if (this.pulseEffects) {
            for (let i = this.pulseEffects.length - 1; i >= 0; i--) {
                const pulse = this.pulseEffects[i];
                const elapsed = now - pulse.startTime;
                
                if (elapsed > pulse.duration) {
                    // Remove pulse
                    this.scene.remove(pulse.mesh);
                    this.pulseEffects.splice(i, 1);
                } else {
                    // Scale up and fade out
                    const progress = elapsed / pulse.duration;
                    const scale = pulse.maxScale * progress;
                    pulse.mesh.scale.set(scale, scale, scale);
                    pulse.mesh.material.opacity = 0.3 * (1 - progress);
                }
            }
        }
        
        // Update electricity effects
        if (this.electricityEffects) {
            for (let i = this.electricityEffects.length - 1; i >= 0; i--) {
                const effect = this.electricityEffects[i];
                const elapsed = now - effect.startTime;
                
                if (elapsed > effect.duration) {
                    // Remove effect
                    this.scene.remove(effect.mesh);
                    this.electricityEffects.splice(i, 1);
                } else {
                    // Fade out
                    const progress = elapsed / effect.duration;
                    effect.mesh.material.opacity = 0.8 * (1 - progress);
                }
            }
        }
        
        // Update neural path signals
        if (this.neuronPaths) {
            this.neuronPaths.forEach(path => {
                for (let i = path.signals.length - 1; i >= 0; i--) {
                    const signal = path.signals[i];
                    
                    // Move signal along path
                    signal.position += signal.speed;
                    
                    // If signal has reached the end
                    if (signal.position >= 1) {
                        // Remove signal
                        path.signals.splice(i, 1);
                        
                        // Activate target region
                        const targetRegion = this.brainRegions[path.target];
                        if (targetRegion) {
                            this.activateComponent(targetRegion.data.component, 0.8);
                        }
                    } else {
                        // Visualize signal as it moves
                        const position = path.curve.getPointAt(signal.position);
                        
                        // Create small flash
                        if (Math.random() < 0.1) { // Only sometimes to avoid too many effects
                            this.createElectricityEffect(
                                position.clone(),
                                path.curve.getPointAt(Math.min(1, signal.position + 0.05))
                            );
                        }
                        
                        // Activate nearby neurons
                        this.neurons.forEach(neuron => {
                            if (neuron.mesh.position.distanceTo(position) < 10 && Math.random() < 0.02) {
                                this.activateNeuron(neuron);
                            }
                        });
                    }
                }
            });
        }
        
        // Update labels position
        this.updateLabels();
        
        // Update health metrics
        this.updateHealthMetrics();
    }

    // Render the scene
    render() {
        this.renderer.render(this.scene, this.camera);
    }

    // Resize handler
    resize() {
        if (!this.container) return;
        
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    // Set up event listeners
    initEventListeners() {
        // Window resize
        window.addEventListener('resize', () => this.resize());
        
        // Mouse events for interaction
        if (this.options.enableInteraction) {
            const container = this.container;
            
            // Mouse move for raycasting
            container.addEventListener('mousemove', (event) => {
                const rect = container.getBoundingClientRect();
                const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
                const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
                
                // Create raycaster
                const raycaster = new THREE.Raycaster();
                raycaster.setFromCamera(new THREE.Vector2(x, y), this.camera);
                
                // Check for intersections with brain regions
                const regionMeshes = Object.values(this.brainRegions).map(r => r.mesh);
                const intersects = raycaster.intersectObjects(regionMeshes);
                
                // Reset all region highlighting
                Object.values(this.brainRegions).forEach(region => {
                    if (!region.isActive) {
                        region.mesh.material.emissiveIntensity = 0;
                    }
                });
                
                // Highlight intersected region
                if (intersects.length > 0) {
                    const intersectedMesh = intersects[0].object;
                    const region = Object.values(this.brainRegions).find(r => r.mesh === intersectedMesh);
                    
                    if (region && !region.isActive) {
                        region.mesh.material.emissiveIntensity = 0.3;
                    }
                }
            });
            
            // Click event to activate region
            container.addEventListener('click', (event) => {
                const rect = container.getBoundingClientRect();
                const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
                const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
                
                // Create raycaster
                const raycaster = new THREE.Raycaster();
                raycaster.setFromCamera(new THREE.Vector2(x, y), this.camera);
                
                // Check for intersections with brain regions
                const regionMeshes = Object.values(this.brainRegions).map(r => r.mesh);
                const intersects = raycaster.intersectObjects(regionMeshes);
                
                // Activate clicked region
                if (intersects.length > 0) {
                    const intersectedMesh = intersects[0].object;
                    const region = Object.values(this.brainRegions).find(r => r.mesh === intersectedMesh);
                    
                    if (region) {
                        this.activateComponent(region.data.component);
                        
                        // Show information about the component
                        if (typeof this.onRegionClick === 'function') {
                            this.onRegionClick(region.data);
                        }
                    }
                }
            });
        }
    }

    // Initialize WebSocket connection for real-time updates
    initWebSocket() {
        try {
            this.socket = io();
            
            // Listen for component activity
            this.socket.on('component_activity', (data) => {
                if (data.component && data.intensity) {
                    this.activateComponent(data.component, data.intensity);
                }
            });
            
            // Listen for health updates
            this.socket.on('health_update', (data) => {
                if (data.metrics) {
                    this.healthMetrics = {
                        ...this.healthMetrics,
                        ...data.metrics,
                        lastUpdate: Date.now()
                    };
                }
            });
            
            // Listen for bulk updates
            this.socket.on('bulk_update', (data) => {
                if (data.components) {
                    data.components.forEach(comp => {
                        if (comp.component && comp.intensity) {
                            // Stagger activation to avoid everything happening at once
                            setTimeout(() => {
                                this.activateComponent(comp.component, comp.intensity);
                            }, Math.random() * 1000);
                        }
                    });
                }
            });
            
            console.log('WebSocket connection established');
        } catch (err) {
            console.warn('WebSocket connection failed:', err);
            // Fall back to simulated updates
            this.startSimulation();
        }
    }

    // Start simulation if WebSocket is not available
    startSimulation() {
        console.log('Starting simulation mode for brain visualization');
        
        // Add pathed neurons
        this.addPathedNeurons();
        
        // Simulate component activation
        setInterval(() => {
            // Get a random component
            const components = Object.values(this.systemMapping).map(m => m.component);
            const randomComponent = components[Math.floor(Math.random() * components.length)];
            
            // Random intensity
            const intensity = 0.5 + Math.random() * 0.5;
            
            // Activate component
            this.activateComponent(randomComponent, intensity);
        }, 3000);
        
        // Simulate connection between components
        setInterval(() => {
            // Get two random regions
            const regions = Object.keys(this.brainRegions);
            const region1 = regions[Math.floor(Math.random() * regions.length)];
            const region2 = regions[Math.floor(Math.random() * regions.length)];
            
            // Skip if same region
            if (region1 === region2) return;
            
            // Create a temporary path
            const path = {
                curve: new THREE.QuadraticBezierCurve3(
                    this.brainRegions[region1].mesh.position.clone(),
                    new THREE.Vector3(0, 0, 0),
                    this.brainRegions[region2].mesh.position.clone()
                ),
                source: region1,
                target: region2,
                signals: []
            };
            
            // Curve through origin for smoother path
            path.curve.v1.copy(this.brainRegions[region1].mesh.position.clone());
            path.curve.v2.set(
                (Math.random() - 0.5) * 20,
                (Math.random() - 0.5) * 20,
                (Math.random() - 0.5) * 20
            );
            path.curve.v3.copy(this.brainRegions[region2].mesh.position.clone());
            
            // Trigger signal
            this.triggerSignalAlongPath(path);
            
            // Add temporary path to list
            if (!this.neuronPaths) this.neuronPaths = [];
            this.neuronPaths.push(path);
            
            // Remove path after signal is done
            setTimeout(() => {
                const index = this.neuronPaths.indexOf(path);
                if (index >= 0) {
                    this.neuronPaths.splice(index, 1);
                }
            }, 5000);
        }, 5000);
    }

    // Get a random color
    getRandomColor() {
        return new THREE.Color(
            Math.random() * 0.5 + 0.5,
            Math.random() * 0.5 + 0.5,
            Math.random() * 0.5 + 0.5
        );
    }

    // Expose method to manually activate a component
    triggerComponent(componentName, intensity = 1.0) {
        this.activateComponent(componentName, intensity);
    }

    // Clean up the visualization
    dispose() {
        // Remove event listeners
        window.removeEventListener('resize', this.resize);
        
        // Dispose of Three.js resources
        this.scene.traverse((object) => {
            if (object.geometry) object.geometry.dispose();
            if (object.material) {
                if (Array.isArray(object.material)) {
                    object.material.forEach(material => material.dispose());
                } else {
                    object.material.dispose();
                }
            }
        });
        
        // Dispose of renderer
        if (this.renderer) {
            this.renderer.dispose();
        }
        
        // Remove DOM elements
        if (this.renderer && this.renderer.domElement) {
            if (this.renderer.domElement.parentNode) {
                this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
            }
        }
        
        // Clean up labels
        if (this.options.showLabels) {
            Object.values(this.brainRegions).forEach(region => {
                if (region.label && region.label.parentNode) {
                    region.label.parentNode.removeChild(region.label);
                }
            });
        }
        
        // Close WebSocket
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BrainVisualization;
}