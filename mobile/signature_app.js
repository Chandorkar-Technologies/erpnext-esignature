// Mobile app JavaScript for signature functionality
class MobileSignatureApp {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.isDrawing = false;
        this.lastX = 0;
        this.lastY = 0;
    }
    
    init() {
        this.setupCanvas();
        this.bindEvents();
    }
    
    setupCanvas() {
        this.canvas = document.getElementById('signature-canvas');
        this.ctx = this.canvas.getContext('2d');
        
        // Set canvas size for mobile
        const container = this.canvas.parentElement;
        this.canvas.width = container.offsetWidth;
        this.canvas.height = 200;
        
        // Configure drawing settings
        this.ctx.lineWidth = 3;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.ctx.strokeStyle = '#000';
    }
    
    bindEvents() {
        // Touch events for mobile
        this.canvas.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
        this.canvas.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        this.canvas.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: false });
        
        // Mouse events for desktop
        this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
        this.canvas.addEventListener('mouseout', this.handleMouseUp.bind(this));
    }
    
    handleTouchStart(e) {
        e.preventDefault();
        const touch = e.touches[0];
        const rect = this.canvas.getBoundingClientRect();
        this.startDrawing(touch.clientX - rect.left, touch.clientY - rect.top);
    }
    
    handleTouchMove(e) {
        e.preventDefault();
        if (!this.isDrawing) return;
        
        const touch = e.touches[0];
        const rect = this.canvas.getBoundingClientRect();
        this.draw(touch.clientX - rect.left, touch.clientY - rect.top);
    }
    
    handleTouchEnd(e) {
        e.preventDefault();
        this.stopDrawing();
    }
    
    handleMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        this.startDrawing(e.clientX - rect.left, e.clientY - rect.top);
    }
    
    handleMouseMove(e) {
        if (!this.isDrawing) return;
        const rect = this.canvas.getBoundingClientRect();
        this.draw(e.clientX - rect.left, e.clientY - rect.top);
    }
    
    handleMouseUp() {
        this.stopDrawing();
    }
    
    startDrawing(x, y) {
        this.isDrawing = true;
        this.lastX = x;
        this.lastY = y;
        this.ctx.beginPath();
        this.ctx.moveTo(x, y);
    }
    
    draw(x, y) {
        this.ctx.lineTo(x, y);
        this.ctx.stroke();
        this.ctx.beginPath();
        this.ctx.moveTo(x, y);
    }
    
    stopDrawing() {
        this.isDrawing = false;
    }
    
    clear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    getSignatureData() {
        return this.canvas.toDataURL('image/png');
    }
    
    isEmpty() {
        const blank = document.createElement('canvas');
        blank.width = this.canvas.width;
        blank.height = this.canvas.height;
        return this.canvas.toDataURL() === blank.toDataURL();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('signature-canvas')) {
        window.signatureApp = new MobileSignatureApp();
        window.signatureApp.init();
    }
});