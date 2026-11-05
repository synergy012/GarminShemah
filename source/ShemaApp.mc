using Toybox.Application;

class ShemaApp extends Application.AppBase {
    var preferences;
    var reader;

    function initialize() { AppBase.initialize(); }
    function onStart(state) { preferences = new Preferences(); }
    function getInitialView() {
        reader = new ReaderView(preferences);
        return [reader, new ReaderDelegate(reader)];
    }
    function onStop(state) {
        if (reader != null) { reader.savePosition(); }
    }
}
