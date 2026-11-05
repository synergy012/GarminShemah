using Toybox.Lang;

// Pixel position belongs to one continuous document, never to a prayer page.
class ReaderState {
    var offset = 0;
    var maximum = 0;

    function initialize(totalHeight, viewport) {
        maximum = totalHeight - viewport;
        if (maximum < 0) { maximum = 0; }
    }

    function move(delta) {
        var old = offset;
        seek(offset + delta);
        return offset != old;
    }

    function seek(value) {
        offset = value;
        if (offset < 0) { offset = 0; }
        if (offset > maximum) { offset = maximum; }
    }

    function firstVisible(lines) {
        var low = 0;
        var high = lines.size();
        while (low < high) {
            var mid = ((low + high) / 2).toNumber();
            var line = lines[mid];
            if (line[1] + line[2] <= offset) { low = mid + 1; }
            else { high = mid; }
        }
        return low;
    }
}
