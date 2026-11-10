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

    // Repeat only the final visible line, including a partially visible line.
    // Subtracting a line height and then rounding down repeats two visible rows.
    function pageTarget(lines, offset, viewport, direction, maximum) {
        if (lines.size() == 0) { return 0; }
        var target = offset;
        for (var i = 0; i < lines.size(); i++) {
            if (direction > 0) {
                if (lines[i][1] >= offset + viewport) { break; }
                if (lines[i][1] + lines[i][2] > offset) { target = lines[i][1]; }
            } else if (lines[i][1] + lines[i][2] > offset) {
                // Put the first current line at the previous screen's bottom.
                target = lines[i][1] + lines[i][2] - viewport;
                break;
            }
        }
        if (direction > 0 && target <= offset) { target = offset + viewport; }
        if (target < 0) { target = 0; }
        if (target > maximum) { target = maximum; }
        return target;
    }
}
