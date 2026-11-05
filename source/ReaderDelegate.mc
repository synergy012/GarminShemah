using Toybox.WatchUi as Ui;
using Toybox.System;

class ReaderDelegate extends Ui.BehaviorDelegate {
    var reader;
    var lastY;
    var lastDragAt = 0;

    function initialize(view) { BehaviorDelegate.initialize(); reader = view; }
    function onNextPage() { reader.scrollBy(38); return true; }
    function onPreviousPage() { reader.scrollBy(-38); return true; }
    function onSelect() { reader.scrollBy(76); return true; }
    function onBack() {
        if (reader.state.offset > 0) { reader.scrollBy(-76); return true; }
        return false;
    }

    function onSwipe(event) {
        // Some device input paths deliver a swipe after drag. Do not scroll twice.
        if (lastDragAt != 0 && System.getTimer() - lastDragAt < 400) { lastY = null; return true; }
        if (event.getDirection() == Ui.SWIPE_UP) { reader.scrollBy(76); return true; }
        if (event.getDirection() == Ui.SWIPE_DOWN) { reader.scrollBy(-76); return true; }
        return false;
    }

    function onTouch(event) {
        lastY = null;
        return true;
    }

    function onDrag(event) {
        var y = event.getCoordinates()[1];
        var now = System.getTimer();
        if (now - lastDragAt > 200) { lastY = null; }
        if (lastY != null) { reader.move(lastY - y); }
        lastY = y;
        lastDragAt = now;
        return true;
    }

    function onMenu() {
        var menu = new Ui.Menu2({:title=>"Reader settings"});
        menu.addItem(new Ui.MenuItem("Return to beginning", null, "begin", null));
        menu.addItem(new Ui.MenuItem("Text size", "Small / medium / large", "sizes", null));
        menu.addItem(new Ui.MenuItem("Nusach", "Ashkenaz / Sefard / Edot", "nusach", null));
        menu.addItem(new Ui.MenuItem("Close reader", null, "exit", null));
        Ui.pushView(menu, new SettingsDelegate(reader, "main"), Ui.SLIDE_IMMEDIATE);
        return true;
    }
}
