using Toybox.Test;

(:test)
function testScrollBounds(logger) {
    var state = new ReaderState(1200, 310);
    state.move(10000);
    Test.assertEqual(state.offset, 890);
    state.move(-10000);
    Test.assertEqual(state.offset, 0);
    return true;
}

(:test)
function testContinuousSectionBoundary(logger) {
    var state = new ReaderState(1200, 310);
    var lines = [[0, 0, 50], [0, 68, 50], [0, 150, 50]];
    state.seek(149);
    Test.assertEqual(state.firstVisible(lines), 2);
    state.move(2);
    Test.assertEqual(state.offset, 151);
    Test.assertEqual(state.firstVisible(lines), 2);
    return true;
}

(:test)
function testFontSizePreservesWordAnchor(logger) {
    var preferences = new Preferences();
    preferences.size = 0;
    var view = new ReaderView(preferences);
    view.state.seek(view.document[:lines][4][1]);
    var anchor = view.currentAnchor();
    preferences.size = 2;
    view.reload(anchor);
    var line = view.document[:lines][view.state.firstVisible(view.document[:lines])];
    Test.assertEqual(line[3], anchor[0]);
    Test.assertEqual(line[4], anchor[1]);
    Test.assert(line[5] <= anchor[2] && line[6] > anchor[2]);
    return true;
}

(:test)
function testRepeatedDocumentTraversal(logger) {
    for (var size = 0; size < 3; size++) {
        var document = DocumentData.load("prototype", size);
        var state = new ReaderState(document[:height], DocumentData.VIEWPORT);
        for (var pass = 0; pass < 100; pass++) {
            while (state.move(38)) {
                Test.assert(state.firstVisible(document[:lines]) < document[:lines].size());
            }
            Test.assertEqual(state.offset, state.maximum);
            while (state.move(-38)) {}
            Test.assertEqual(state.offset, 0);
        }
    }
    return true;
}
