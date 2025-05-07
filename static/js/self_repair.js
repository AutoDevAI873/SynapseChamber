/**
 * Synapse Chamber Self-Repair System
 * 
 * This script implements defensive programming techniques to recover from 
 * common DOM and JavaScript errors. It provides safety wrappers around
 * DOM operations and helps ensure application stability.
 */

console.log("Synapse Self-Repair System initialized");

// Initialize global safety wrapper
window.SynapseSelfRepair = {
    // Safe element finder - never returns null, returns a proxy that safely handles calls
    findElement: function(selector, parent = document) {
        const element = parent ? parent.querySelector(selector) : null;
        if (!element) {
            console.warn(`SynapseSelfRepair: Element not found: ${selector}`);
            // Return a proxy that silently catches operations on a null element
            return new Proxy({}, {
                get: function(target, prop) {
                    if (prop === 'addEventListener') {
                        // Return a no-op function for addEventListener
                        return function() { 
                            console.warn(`SynapseSelfRepair: Attempted to add event listener to non-existent element: ${selector}`);
                            return false; 
                        };
                    }
                    if (prop === 'classList') {
                        // Return a classList proxy with no-op functions
                        return {
                            add: function() {},
                            remove: function() {},
                            toggle: function() {},
                            contains: function() { return false; }
                        };
                    }
                    if (prop === 'style') {
                        // Return a style proxy that does nothing
                        return new Proxy({}, {
                            set: function() { return true; },
                            get: function() { return ''; }
                        });
                    }
                    if (typeof target[prop] === 'function') {
                        return function() { return null; };
                    }
                    return null;
                },
                set: function() {
                    console.warn(`SynapseSelfRepair: Attempted to set property on non-existent element: ${selector}`);
                    return true;
                }
            });
        }
        return element;
    },
    
    // Find all elements safely, returning empty array instead of null
    findAllElements: function(selector, parent = document) {
        if (!parent) return [];
        return Array.from(parent.querySelectorAll(selector) || []);
    },
    
    // Safely add event listener, checking if element and method exist
    addEventListenerSafe: function(selector, event, callback, useCapture = false) {
        const element = this.findElement(selector);
        if (element && element.addEventListener) {
            element.addEventListener(event, function(e) {
                try {
                    callback(e);
                } catch (error) {
                    console.error(`SynapseSelfRepair: Error in event listener for ${selector}:`, error);
                }
            }, useCapture);
            return true;
        }
        return false;
    },
    
    // Safely execute a function, catching errors
    safeExec: function(fn, ...args) {
        try {
            return fn(...args);
        } catch (error) {
            console.error("SynapseSelfRepair: Error executing function:", error);
            return null;
        }
    },
    
    // Fix common issues with the application
    runRepairs: function() {
        // Fix for missing notification container
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.style.position = 'fixed';
            container.style.top = '10px';
            container.style.right = '10px';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
            console.log("SynapseSelfRepair: Created missing notification container");
        }
        
        // Fix for missing Chart.instances
        if (typeof Chart !== 'undefined' && !Chart.instances) {
            Chart.instances = [];
            Chart.instances.forEach = function() { /* Empty function */ };
            console.log("SynapseSelfRepair: Fixed missing Chart.instances");
        }
        
        // Fix for toggleDockBtn on pages where it shouldn't be active
        const toggleDockBtn = document.getElementById('toggleDockBtn');
        if (toggleDockBtn && window.location.pathname !== '/dashboard') {
            toggleDockBtn.style.display = 'none';
            console.log("SynapseSelfRepair: Hiding dock toggle button on non-dashboard page");
        }
        
        // Fix for data-bs-target attributes without matching elements
        document.querySelectorAll('[data-bs-target]').forEach(element => {
            const targetId = element.getAttribute('data-bs-target');
            if (targetId && targetId.startsWith('#') && !document.querySelector(targetId)) {
                console.warn(`SynapseSelfRepair: Found data-bs-target pointing to non-existent element: ${targetId}`);
                // Optionally create the target element as a fallback
            }
        });
    }
};

// Run repairs on page load
document.addEventListener('DOMContentLoaded', function() {
    // Allow time for other scripts to initialize
    setTimeout(function() {
        SynapseSelfRepair.runRepairs();
    }, 500);
});

// Run repairs again when navigating between pages via AJAX
if (typeof window.addEventListener === 'function') {
    window.addEventListener('load', function() {
        SynapseSelfRepair.runRepairs();
    });
}

// Intercept common JavaScript errors
window.addEventListener('error', function(e) {
    console.warn('SynapseSelfRepair: Caught error:', e.message);
    // Don't prevent the error from propagating
    return false;
});