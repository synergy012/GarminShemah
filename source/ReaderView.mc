using Toybox.Graphics;
using Toybox.Lang;
using Toybox.Timer;
using Toybox.System;
using Toybox.WatchUi as Ui;

class ReaderView extends Ui.View {
    var preferences;
    var state;
    var document;
    var documentId;
    var cache;
    var saveTimer;
    var animationTimer;
    var targetOffset = 0;

    function initialize(prefs) {
        View.initialize();
        preferences = prefs;
        cache = {};
        saveTimer = new Timer.Timer();
        animationTimer = new Timer.Timer();
        reload(null);
        var stored = preferences.readPosition(documentId);
        if (stored != null) {
            if (stored.hasKey("size") && stored["size"] == preferences.size) {
                state.seek(stored["offset"]);
            } else if (stored.hasKey("anchor")) { restoreAnchor(stored["anchor"]); }
        }
        if (DocumentData.PROTOTYPE || DocumentData.REVIEW) { System.println("Reader restored " + documentId + " offset=" + state.offset.toString() + " size=" + preferences.size.toString()); }
    }

    function reload(anchor) {
        animationTimer.stop();
        cache = {};
        // The prototype is explicitly labelled and never impersonates an unavailable nusach.
        documentId = DocumentData.PROTOTYPE ? "prototype" : preferences.nusach;
        document = DocumentData.load(documentId, preferences.size);
        var height = document == null ? 0 : document[:height];
        state = new ReaderState(height, DocumentData.VIEWPORT);
        if (anchor != null) { restoreAnchor(anchor); }
    }

    function currentAnchor() {
        if (document == null) { return null; }
        var lines = document[:lines];
        var i = state.firstVisible(lines);
        if (i >= lines.size()) { return null; }
        var line = lines[i];
        return [line[3], line[4], line[5]];
    }

    function restoreAnchor(anchor) {
        if (document == null || !(anchor instanceof Lang.Array) || anchor.size() != 3) { return; }
        if (!(anchor[0] instanceof Lang.String) || !(anchor[1] instanceof Lang.Number) || !(anchor[2] instanceof Lang.Number)) { return; }
        var lines = document[:lines];
        for (var i = 0; i < lines.size(); i++) {
            var line = lines[i];
            if (line[3].equals(anchor[0]) && line[4] == anchor[1] && line[5] <= anchor[2] && line[6] > anchor[2]) {
                state.seek(line[1]);
                return;
            }
        }
        // Content edits may invalidate the word anchor. Resume at that section's heading.
        for (var j = 0; j < lines.size(); j++) {
            if (lines[j][3].equals(anchor[0])) { state.seek(lines[j][1]); return; }
        }
    }

    function move(delta) {
        animationTimer.stop();
        if (state.move(delta)) {
            saveTimer.stop();
            saveTimer.start(method(:savePosition), 1500, false);
            Ui.requestUpdate();
        }
    }

    function scrollBy(delta) {
        animationTimer.stop();
        targetOffset = state.offset + delta;
        if (targetOffset < 0) { targetOffset = 0; }
        if (targetOffset > state.maximum) { targetOffset = state.maximum; }
        if (targetOffset != state.offset) { animationTimer.start(method(:animate), 50, true); }
    }

    function animate() {
        var delta = targetOffset - state.offset;
        if (delta > 8) { delta = 8; }
        if (delta < -8) { delta = -8; }
        state.move(delta);
        Ui.requestUpdate();
        if (state.offset == targetOffset) {
            animationTimer.stop();
            saveTimer.stop();
            saveTimer.start(method(:savePosition), 1500, false);
        }
    }

    function beginning() {
        animationTimer.stop();
        state.seek(0);
        cache = {};
        savePosition();
        Ui.requestUpdate();
    }

    function savePosition() {
        preferences.savePosition(documentId, state.offset, currentAnchor());
        if (DocumentData.PROTOTYPE || DocumentData.REVIEW) { System.println("Reader saved " + documentId + " offset=" + state.offset.toString() + " size=" + preferences.size.toString()); }
    }

    function onHide() {
        animationTimer.stop();
        saveTimer.stop();
        savePosition();
        cache = {};
    }

    function onUpdate(dc) {
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_BLACK);
        dc.clear();
        dc.setColor(0xf2e6cd, Graphics.COLOR_BLACK);
        var width = dc.getWidth();
        var top = ((dc.getHeight() - DocumentData.VIEWPORT) / 2).toNumber();
        var left = ((width - DocumentData.WIDTH) / 2).toNumber();
        if (DocumentData.PROTOTYPE) {
            dc.drawText(width / 2, 32, Graphics.FONT_XTINY, "NOT PRAYER", Graphics.TEXT_JUSTIFY_CENTER);
        } else if (DocumentData.REVIEW) {
            dc.drawText(width / 2, 32, Graphics.FONT_XTINY, "REVIEW COPY", Graphics.TEXT_JUSTIFY_CENTER);
        }
        if (document == null) {
            dc.drawText(width / 2, dc.getHeight() / 2, Graphics.FONT_XTINY, "Text unavailable", Graphics.TEXT_JUSTIFY_CENTER);
            return;
        }
        var lines = document[:lines];
        var first = state.firstVisible(lines);
        var last = first;
        while (last < lines.size() && lines[last][1] < state.offset + DocumentData.VIEWPORT) { last++; }
        // Evict hidden bitmaps before loading the next visible window.
        var visible = {};
        for (var v = first; v < last; v++) { visible[lines[v][0]] = true; }
        var oldKeys = cache.keys();
        for (var k = 0; k < oldKeys.size(); k++) {
            var key = oldKeys[k];
            if (!visible.hasKey(key)) { cache.remove(key); }
        }
        for (var i = first; i < last; i++) {
            var resource = lines[i][0];
            if (!cache.hasKey(resource)) { cache[resource] = Ui.loadResource(resource); }
            var destinationY = top + lines[i][1] - state.offset;
            var clipTop = destinationY < top ? top : destinationY;
            var clipBottom = destinationY + lines[i][2];
            if (clipBottom > top + DocumentData.VIEWPORT) { clipBottom = top + DocumentData.VIEWPORT; }
            dc.setClip(left, clipTop, DocumentData.WIDTH, clipBottom - clipTop);
            // Palette resources cannot be source-cropped by drawBitmap2 on this
            // target. Destination clipping keeps indexed atlases and exact glyphs.
            dc.drawBitmap(left, destinationY - lines[i][7], cache[resource]);
        }
        dc.clearClip();
    }
}
