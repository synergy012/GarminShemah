using Toybox.Attention;
using Toybox.System;

module DisplayBrightness {
    function label(level) {
        var labels = ["System", "10%", "25%", "50%", "100%"];
        return labels[level];
    }

    function apply(level) {
        var levels = [true, 0.1, 0.25, 0.5, 1.0];
        // Apply on selection/reader entry, never from a repeating timer or redraw.
        // Garmin retains its own display timeout and burn-in protection.
        try { Attention.backlight(levels[level]); }
        catch (error) { System.println("Brightness deferred to device display protection"); }
    }
}
