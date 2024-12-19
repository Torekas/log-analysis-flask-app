// Helper to show Bootstrap Toast notifications
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    const toastId = `toast-${Date.now()}`;
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>`;
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const toast = new bootstrap.Toast(document.getElementById(toastId));
    toast.show();
}

// Helper to control the loading bar
function showLoadingBar(show = true) {
    const loadingBar = document.getElementById('loadingBar');
    loadingBar.style.display = show ? 'block' : 'none';
}

// Easing function for smooth animations
function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
}

// Point class to handle animation and interactions
class Point {
    constructor(point_id, x, y) {
        this.point_id = point_id;
        this.x = x;
        this.y = y;
        this.baseRadius = 5;
        this.currentRadius = 0;
        this.targetRadius = this.baseRadius;
        this.animationSpeed = 0.05; // Speed for grow animation
        this.isAnimating = true;

        // Interaction states
        this.state = 'normal'; // 'normal', 'hovered', 'clicked'
        this.hoverRadius = 8;
        this.clickRadius = 10;
        this.currentTargetRadius = this.baseRadius;
    }

    // Initialize point appearance animation
    updateAppearance() {
        if (this.currentRadius < this.targetRadius) {
            this.currentRadius += this.animationSpeed;
            if (this.currentRadius >= this.targetRadius) {
                this.currentRadius = this.targetRadius;
                this.isAnimating = false;
            }
        }
    }

    // Handle state transitions for interactions
    updateInteraction(mouseX, mouseY) {
        const dx = this.x - mouseX;
        const dy = this.y - mouseY;
        const distanceSq = dx * dx + dy * dy;
        const hoverThreshold = this.currentTargetRadius + 5; // Allow some tolerance
        const isHover = distanceSq <= hoverThreshold * hoverThreshold;

        if (isHover) {
            if (this.state !== 'hovered') {
                this.state = 'hovered';
                this.currentTargetRadius = this.hoverRadius;
            }
        } else {
            if (this.state !== 'normal') {
                this.state = 'normal';
                this.currentTargetRadius = this.baseRadius;
            }
        }
    }

    // Handle click state
    handleClick() {
        this.state = 'clicked';
        this.currentTargetRadius = this.clickRadius;

        // Reset to 'normal' after a short delay
        setTimeout(() => {
            this.state = 'normal';
            this.currentTargetRadius = this.baseRadius;
        }, 300); // 300ms for click animation
    }

    // Update radius smoothly towards target
    updateRadius() {
        if (this.currentRadius < this.currentTargetRadius) {
            this.currentRadius += 0.2;
            if (this.currentRadius > this.currentTargetRadius) {
                this.currentRadius = this.currentTargetRadius;
            }
        } else if (this.currentRadius > this.currentTargetRadius) {
            this.currentRadius -= 0.2;
            if (this.currentRadius < this.currentTargetRadius) {
                this.currentRadius = this.currentTargetRadius;
            }
        }
    }

    draw(ctx) {
        ctx.beginPath();
        ctx.fillStyle = this.getColor();
        ctx.arc(this.x, this.y, this.currentRadius, 0, 2 * Math.PI);
        ctx.fill();
    }

    getColor() {
        switch (this.state) {
            case 'hovered':
                return 'orange';
            case 'clicked':
                return 'green';
            default:
                return 'red';
        }
    }
}

document.getElementById('downloadPdfBtn').addEventListener('click', function () {
    showToast('PDF download started. Please wait...', 'primary');
    showLoadingBar(true);

    fetch("/download_pdf")
        .then(response => {
            if (response.ok) {
                window.location.href = "/download_pdf";
                showToast('PDF successfully downloaded!', 'success');
            } else {
                showToast('Failed to download PDF. Please try again.', 'danger');
            }
        })
        .catch(() => showToast('An error occurred while downloading the PDF.', 'danger'))
        .finally(() => showLoadingBar(false));
});

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('halfCircleCanvas');
    const ctx = canvas.getContext('2d');


    showLoadingBar(true);
    showToast('Fetching point data...', 'info');

    fetch('/get_points_data')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                showToast(data.error, 'danger');
                showLoadingBar(false);
                return;
            }
            showToast('Point data loaded successfully!', 'success');
            showLoadingBar(false);

            const { points, distances, angles_per_distance } = data;
            const centerX = canvas.width / 2;
            const baseY = canvas.height - 10;
            const radiusStep = 40;

            // Define a color palette for the arcs
            const arcColors = ['#FF5733', '#33FF57', '#3357FF', '#F1C40F', '#9B59B6'];

            // Updated drawArcs function with labels
            // Updated drawArcs function without labels
            function drawArcs() {
                distances.forEach((dist, distIndex) => {
                    const r = radiusStep * (distIndex + 1);
                    const color = arcColors[distIndex % arcColors.length]; // Cycle through colors if more arcs than colors
                    ctx.strokeStyle = color;
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(centerX, baseY, r, Math.PI, 0, false);
                    ctx.stroke();

                    // Distance labels have been removed
                });
            }


            drawArcs();


            function drawLegend() {
                const legendPadding = 10;
                const boxSize = 20;
                const textSpacing = 8;
                const fontSize = 14;
                ctx.font = `${fontSize}px Arial`;
                ctx.textBaseline = 'middle';
                ctx.textAlign = 'left';

                // Calculate legend position
                const legendX = centerX + radiusStep * distances.length + 40; // 40px to the right of the largest arc
                let legendY = baseY - radiusStep * distances.length; // Start aligned with the top of the half-circle

                distances.forEach((dist, distIndex) => {
                    const color = arcColors[distIndex % arcColors.length];

                    // Draw color box
                    ctx.fillStyle = color;
                    ctx.fillRect(legendX, legendY, boxSize, boxSize);

                    // Draw distance text
                    ctx.fillStyle = '#000'; // Black color for text
                    ctx.fillText(`${dist} cm`, legendX + boxSize + textSpacing, legendY + boxSize / 2);

                    // Update Y position for next legend item
                    legendY += boxSize + 10; // 10px space between items
                });

                // Optional: Draw a border around the legend
                const legendHeight = distances.length * (boxSize + 10) - 10; // Total height based on items
                ctx.strokeStyle = '#000'; // Black border
                ctx.lineWidth = 1;
                ctx.strokeRect(legendX - legendPadding, baseY - radiusStep * distances.length - legendPadding,  boxSize + 100, legendHeight + legendPadding * 2);
            }

            // Function to draw degree markers
            function drawDegreeMarkers() {
                const degrees = [0, 45, 90, 135, 180];
                const markerLength = 10; // Length of the marker lines
                ctx.strokeStyle = '#000'; // Marker line color
                ctx.fillStyle = '#000'; // Marker label color
                ctx.lineWidth = 1;
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';

                degrees.forEach(degree => {
                    const rad = (degree * Math.PI) / 180;
                    const xStart = centerX + (radiusStep * distances.length + 20) * Math.cos(Math.PI - rad);
                    const yStart = baseY - (radiusStep * distances.length + 20) * Math.sin(Math.PI - rad);
                    const xEnd = centerX + (radiusStep * distances.length + 20 + markerLength) * Math.cos(Math.PI - rad);
                    const yEnd = baseY - (radiusStep * distances.length + 20 + markerLength) * Math.sin(Math.PI - rad);

                    // Draw marker line
                    ctx.beginPath();
                    ctx.moveTo(xStart, yStart);
                    ctx.lineTo(xEnd, yEnd);
                    ctx.stroke();

                    // Calculate label position slightly beyond the marker end
                    const labelX = centerX + (radiusStep * distances.length + 35) * Math.cos(Math.PI - rad);
                    const labelY = baseY - (radiusStep * distances.length + 35) * Math.sin(Math.PI - rad);

                    // Draw degree label
                    ctx.fillText(`${degree}°`, labelX, labelY);
                });
            }


            // Create Point objects
            let animatedPoints = [];
            points.forEach(p => {
                const { point_id, distance, angle } = p;
                const distIndex = distances.indexOf(distance);
                const r = radiusStep * (distIndex + 1);
                const radAngle = angle * Math.PI / 180;
                const radPlacement = Math.PI - radAngle;

                const x = centerX + r * Math.cos(radPlacement);
                const y = baseY - r * Math.sin(radPlacement);

                animatedPoints.push(new Point(point_id, x, y));
            });

            // Animation variables
            let animationRequestId;
            let currentPointIndex = 0;
            const animationDelay = 200; // Time between points in ms
            let lastPointTime = Date.now();

            // Mouse position
            let mouseX = -1;
            let mouseY = -1;

            // Handle mouse movement
            canvas.addEventListener('mousemove', function (e) {
                const rect = canvas.getBoundingClientRect();
                mouseX = e.clientX - rect.left;
                mouseY = e.clientY - rect.top;

                // Update interaction states
                animatedPoints.forEach(p => p.updateInteraction(mouseX, mouseY));
            });

            // Handle mouse out to reset hover states
            canvas.addEventListener('mouseout', function () {
                mouseX = -1;
                mouseY = -1;
                animatedPoints.forEach(p => {
                    if (p.state !== 'clicked') {
                        p.state = 'normal';
                        p.currentTargetRadius = p.baseRadius;
                    }
                });
            });

            function animatePoints() {
                const now = Date.now();
                // Add points one by one based on the delay
                while (currentPointIndex < animatedPoints.length && now - lastPointTime >= animationDelay) {
                    currentPointIndex++;
                    lastPointTime = now;
                }

                // Clear the canvas before redrawing
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Redraw arcs and degree markers
                drawArcs();
                drawDegreeMarkers();
                drawLegend();

                // Update and draw points
                animatedPoints.slice(0, currentPointIndex).forEach(point => {
                    if (point.isAnimating) {
                        point.updateAppearance();
                    }
                    point.updateRadius();
                    point.draw(ctx);
                });

                // Continue the animation if there are still points to animate
                if (currentPointIndex < animatedPoints.length || animatedPoints.some(p => p.isAnimating || p.state !== 'normal')) {
                    animationRequestId = requestAnimationFrame(animatePoints);
                }
            }


            // Start the animation
            animatePoints();

            let pointPositions = animatedPoints; // For click detection

            canvas.addEventListener('click', function (e) {
                const rect = canvas.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                const clickY = e.clientY - rect.top;

                for (let p of pointPositions) {
                    let dx = p.x - clickX;
                    let dy = p.y - clickY;
                    if (dx * dx + dy * dy <= p.currentTargetRadius * p.currentTargetRadius) {
                        // Trigger click animation
                        p.handleClick();

                        showToast(`Loading analysis for point ${p.point_id}...`, 'info');
                        showLoadingBar(true);

                        fetch(`/get_point_data?point_id=${p.point_id}`)
                            .then(response => response.json())
                            .then(d => {
                                document.getElementById('pointTitle').textContent = d.title || '';
                                document.getElementById('pointDescription').textContent = d.description || '';
                                document.getElementById('chartImage').src = d.chart_url || '';
                                document.getElementById('pointData').style.display = 'block';
                                showToast('Analysis loaded successfully!', 'success');
                            })
                            .catch(() => showToast('Failed to load analysis. Please try again.', 'danger'))
                            .finally(() => showLoadingBar(false));
                        break;
                    }
                }
            });
        })
        .catch(() => {
            showToast('Failed to load point data. Please try again.', 'danger');
            showLoadingBar(false);
        });
});
