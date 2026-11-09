using Toybox.Graphics;
using Toybox.WatchUi as Ui;

// Offline attribution accompanies every standalone PRG containing licensed text.
class SourcesView extends Ui.View {
    var lines;
    var offset = 0;
    var maximum = 0;
    function initialize() { View.initialize(); }
    function move(delta) {
        offset += delta;
        if (offset < 0) { offset = 0; }
        if (offset > maximum) { offset = maximum; }
        Ui.requestUpdate();
    }
    function onUpdate(dc) {
        var font = Graphics.FONT_XTINY;
        var step = dc.getFontHeight(font) + 6;
        var width = DocumentData.WIDTH;
        var top = (dc.getHeight() - DocumentData.VIEWPORT) / 2;
        var left = (dc.getWidth() - width) / 2;
        if (lines == null) {
            lines = [];
            var paragraphs = DocumentData.sourceLines();
            for (var p = 0; p < paragraphs.size(); p++) {
                var text = paragraphs[p];
                var line = "";
                var space = -1;
                for (var i = 0; i < text.length(); i++) {
                    var character = text.substring(i, i + 1);
                    if (dc.getTextWidthInPixels(line + character, font) > width) {
                        if (space >= 0) {
                            lines.add(line.substring(0, space));
                            line = line.substring(space + 1, line.length());
                        } else { lines.add(line); line = ""; }
                        space = -1;
                    }
                    if (character.equals(" ")) { space = line.length(); }
                    line += character;
                }
                if (line.length() > 0) { lines.add(line); }
                lines.add("");
            }
            maximum = lines.size() * step - DocumentData.VIEWPORT;
            if (maximum < 0) { maximum = 0; }
        }
        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_BLACK);
        dc.clear();
        dc.setColor(0xf2e6cd, Graphics.COLOR_BLACK);
        dc.setClip(left, top, width, DocumentData.VIEWPORT);
        for (var j = 0; j < lines.size(); j++) {
            var y = top + j * step - offset;
            if (y + step > top && y < top + DocumentData.VIEWPORT) {
                dc.drawText(left, y, font, lines[j], Graphics.TEXT_JUSTIFY_LEFT);
            }
        }
        dc.clearClip();
    }
}

class SourcesDelegate extends Ui.BehaviorDelegate {
    var view;
    function initialize(sourceView) { BehaviorDelegate.initialize(); view = sourceView; }
    function onNextPage() { view.move(90); return true; }
    function onPreviousPage() { view.move(-90); return true; }
    function onBack() { Ui.popView(Ui.SLIDE_IMMEDIATE); return true; }
}
