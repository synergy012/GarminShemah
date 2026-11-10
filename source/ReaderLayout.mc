// Filter already-shaped lines; source text and bitmaps remain unchanged.
module ReaderLayout {
    function filter(document, instructions, fullShema) {
        if (document == null) { return null; }
        var original = document[:lines];
        var kept = [];
        var previousEnd = 0;
        var y = 0;
        for (var i = 0; i < original.size(); i++) {
            var line = original[i];
            var gap = line[1] - previousEnd;
            previousEnd = line[1] + line[2];
            var flags = line[8];
            if ((!instructions && (flags & 1) != 0) || (!fullShema && (flags & 2) != 0)) { continue; }
            y += gap;
            line[1] = y;
            kept.add(line);
            y += line[2];
        }
        return {:lines=>kept, :height=>y + document[:height] - previousEnd};
    }

    // A screen step retains one line of context and lands at a whole-line boundary.
    function pageTarget(lines, offset, viewport, direction, maximum) {
        if (lines.size() == 0) { return 0; }
        var height = lines[0][2];
        var step = viewport - height;
        if (step <= 0) { step = viewport; }
        var desired = offset + direction * step;
        if (desired <= 0) { return 0; }
        if (desired >= maximum) { return maximum; }
        var target = desired;
        for (var i = 0; i < lines.size(); i++) {
            if (direction > 0) {
                if (lines[i][1] > desired) { break; }
                if (lines[i][1] > offset) { target = lines[i][1]; }
            } else if (lines[i][1] >= desired) {
                if (lines[i][1] < offset) { target = lines[i][1]; }
                break;
            }
        }
        return target;
    }
}
