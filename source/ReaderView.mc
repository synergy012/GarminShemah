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

    function onShow() { DisplayBrightness.apply(preferences.brightness); }

    function initialize(prefs) {
        View.initialize();
        preferences = prefs;
        cache = {};
        saveTimer = new Timer.Timer();
        reload(null);
        var stored = preferences.readPosition(documentId);
        if (stored != null) {
            if (preferences.sameLayout(stored)) {
                state.seek(stored["offset"]);
            } else if (stored.hasKey("anchor")) { restoreAnchor(stored["anchor"]); }
        }
        if (DocumentData.PROTOTYPE || DocumentData.REVIEW) { System.println("Reader restored " + documentId + " offset=" + state.offset.toString() + " size=" + preferences.size.toString()); }
    }

    function reload(anchor) {
        cache = {};
        // The prototype is explicitly labelled and never impersonates an unavailable nusach.
        documentId = DocumentData.PROTOTYPE ? "prototype" : preferences.nusach;
        document = ReaderLayout.filter(DocumentData.load(documentId, preferences.size), preferences.showInstructions, preferences.fullShema);
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
        // If a setting hides the current passage, continue with the following
        // visible paragraph/section instead of jumping to the document beginning.
        for (var j = 0; j < lines.size(); j++) {
            var order = lines[j][3].compareTo(anchor[0]);
            if (order > 0 || (order == 0 && lines[j][4] >= anchor[1])) {
                state.seek(lines[j][1]); return;
            }
        }
        state.seek(state.maximum);
    }

    function move(delta) {
        if (state.move(delta)) {
            saveTimer.stop();
            saveTimer.start(method(:savePosition), 1500, false);
            Ui.requestUpdate();
        }
    }

    function advance(direction) {
        if (document == null) { return; }
        if (preferences.screenScroll) {
            var target = ReaderLayout.pageTarget(document[:lines], state.offset, DocumentData.VIEWPORT, direction, state.maximum);
            move(target - state.offset);
        } else {
            var first = state.firstVisible(document[:lines]);
            var height = first < document[:lines].size() ? document[:lines][first][2] : 38;
            move(direction * height);
        }
    }

    function beginning() {
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
        // Left-side arc sits outside the Hebrew reading rectangle.
        var radius = width / 2 - 11;
        dc.setPenWidth(3);
        dc.setColor(0x303030, Graphics.COLOR_BLACK);
        dc.drawArc(width / 2, dc.getHeight() / 2, radius, Graphics.ARC_COUNTER_CLOCKWISE, 140, 220);
        var sweep = (80 * state.progress()).toNumber();
        // Equal/truncated arc angles draw a full circle in this SDK.
        if (sweep > 0) {
            dc.setColor(0xf2e6cd, Graphics.COLOR_BLACK);
            dc.drawArc(width / 2, dc.getHeight() / 2, radius, Graphics.ARC_COUNTER_CLOCKWISE, 140, 140 + sweep);
        }
        dc.setPenWidth(1);
    }
}
