using Toybox.Test;

function overlappingRows(lines, before, after) {
    var count = 0;
    for (var i = 0; i < lines.size(); i++) {
        var line = lines[i];
        if (line[1] < before + DocumentData.VIEWPORT && line[1] + line[2] > before &&
            line[1] < after + DocumentData.VIEWPORT && line[1] + line[2] > after) { count++; }
    }
    return count;
}

(:test)
function testPartialRowDoesNotCauseTwoRowOverlap(logger) {
    var lines = [];
    for (var i = 0; i < 30; i++) { lines.add([0, 12 + i * 53, 53]); }
    var next = ReaderLayout.pageTarget(lines, 12, 310, 1, 1300);
    Test.assertEqual(next, 277);
    Test.assertEqual(overlappingRows(lines, 12, next), 1);
    var previous = ReaderLayout.pageTarget(lines, next, 310, -1, 1300);
    Test.assertEqual(previous, 20);
    Test.assertEqual(overlappingRows(lines, next, previous), 1);
    return true;
}

(:test)
function testProgressTracksDocumentBounds(logger) {
    var state = new ReaderState(1000, 310);
    Test.assertEqual(state.progress(), 0.0);
    state.seek(345);
    Test.assertEqual(state.progress(), 0.5);
    state.seek(10000);
    Test.assertEqual(state.progress(), 1.0);
    state.seek(-100);
    Test.assertEqual(state.progress(), 0.0);
    var shortDocument = new ReaderState(200, 310);
    Test.assertEqual(shortDocument.progress(), 1.0);
    return true;
}

(:test)
function testReaderVisibilityOptions(logger) {
    var ids = DocumentData.PROTOTYPE ? ["prototype"] : ["ashkenaz", "sefard", "edot_hamizrach"];
    for (var id = 0; id < ids.size(); id++) {
      for (var size = 0; size < 3; size++) {
        for (var option = 0; option < 4; option++) {
            var instructions = (option & 1) != 0;
            var shema = (option & 2) != 0;
            var full = DocumentData.load(ids[id], size);
            var expected = [];
            for (var i = 0; i < full[:lines].size(); i++) {
                var line = full[:lines][i];
                if ((!instructions && (line[8] & 1) != 0) || (!shema && (line[8] & 2) != 0)) { continue; }
                expected.add(line[3] + ":" + line[4].toString() + ":" + line[5].toString());
            }
            var filtered = ReaderLayout.filter(full, instructions, shema);
            Test.assertEqual(filtered[:lines].size(), expected.size());
            var end = 0;
            for (var j = 0; j < expected.size(); j++) {
                var kept = filtered[:lines][j];
                Test.assertEqual(kept[3] + ":" + kept[4].toString() + ":" + kept[5].toString(), expected[j]);
                Test.assert(kept[1] >= end && kept[1] - end < 100);
                end = kept[1] + kept[2];
            }
            Test.assert(filtered[:height] >= end && filtered[:height] - end < 100);
        }
      }
    }
    return true;
}

(:test)
function testScreenStepsAreImmediateAndOverlap(logger) {
    var prefs = new Preferences();
    prefs.showInstructions = false;
    prefs.fullShema = true;
    prefs.screenScroll = true;
    var ids = DocumentData.PROTOTYPE ? ["prototype"] : ["ashkenaz", "sefard", "edot_hamizrach"];
    for (var id = 0; id < ids.size(); id++) {
      prefs.nusach = ids[id];
      for (var size = 0; size < 3; size++) {
        prefs.size = size;
        var view = new ReaderView(prefs);
        view.beginning();
        while (view.state.offset < view.state.maximum) {
            var old = view.state.offset;
            view.advance(1);
            Test.assert(view.state.offset > old);
            Test.assert(view.state.offset - old <= DocumentData.VIEWPORT);
            // Terminal clamping can repeat more rows to keep the final page full.
            if (view.state.offset < view.state.maximum) {
                Test.assertEqual(overlappingRows(view.document[:lines], old, view.state.offset), 1);
            }
        }
        while (view.state.offset > 0) {
            var previous = view.state.offset;
            view.advance(-1);
            Test.assert(view.state.offset < previous);
            Test.assert(previous - view.state.offset <= DocumentData.VIEWPORT);
            if (view.state.offset > 0) {
                Test.assertEqual(overlappingRows(view.document[:lines], previous, view.state.offset), 1);
            }
        }
        prefs.screenScroll = false;
        view.advance(1);
        Test.assertEqual(view.state.offset, view.document[:lines][0][2]);
        prefs.screenScroll = true;
        view.onHide();
      }
    }
    return true;
}

(:test)
function testOptionsMigrateAndHiddenAnchorContinues(logger) {
    var prefs = new Preferences();
    prefs.showInstructions = false;
    prefs.fullShema = true;
    prefs.size = 0;
    Test.assert(!prefs.sameLayout({"size"=>0}));
    Test.assert(!prefs.sameLayout({"size"=>0, "showInstructions"=>false, "fullShema"=>true}));
    Test.assert(prefs.sameLayout({"size"=>0, "showInstructions"=>false, "fullShema"=>true, "textVersion"=>DocumentData.TEXT_VERSION}));
    if (DocumentData.PROTOTYPE) { return true; }
    prefs.nusach = "ashkenaz";
    prefs.showInstructions = true;
    var view = new ReaderView(prefs);
    for (var i = 0; i < view.document[:lines].size(); i++) {
        if (view.document[:lines][i][3].equals("source-008")) {
            view.state.seek(view.document[:lines][i][1]); break;
        }
    }
    var anchor = view.currentAnchor();
    prefs.fullShema = false;
    view.reload(anchor);
    var next = view.document[:lines][view.state.firstVisible(view.document[:lines])];
    Test.assertEqual(next[3], "source-010");
    view.onHide();
    return true;
}

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
    var ids = DocumentData.PROTOTYPE ? ["prototype"] : ["ashkenaz", "sefard", "edot_hamizrach"];
    var passes = DocumentData.PROTOTYPE ? 100 : 3;
    for (var id = 0; id < ids.size(); id++) {
      for (var size = 0; size < 3; size++) {
        var document = DocumentData.load(ids[id], size);
        var state = new ReaderState(document[:height], DocumentData.VIEWPORT);
        for (var pass = 0; pass < passes; pass++) {
            while (state.move(38)) {
                Test.assert(state.firstVisible(document[:lines]) < document[:lines].size());
            }
            Test.assertEqual(state.offset, state.maximum);
            while (state.move(-38)) {}
            Test.assertEqual(state.offset, 0);
        }
      }
    }
    return true;
}
