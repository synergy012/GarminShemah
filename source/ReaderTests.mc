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
