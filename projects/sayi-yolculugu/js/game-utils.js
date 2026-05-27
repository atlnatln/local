function normalizeWall(w) {
  if (Array.isArray(w)) return {x: w[0], y: w[1], type: 'full', blocks: []};
  return {x: w.x, y: w.y, type: w.type || 'full', blocks: w.blocks || []};
}

function buildWallMap(lv) {
  var map = {};
  (lv.walls || []).forEach(function(w) {
    var nw = normalizeWall(w);
    map[nw.x + ',' + nw.y] = nw;
  });
  return map;
}

function sleep(ms) { return new Promise(function(r) { setTimeout(r, ms); }); }
