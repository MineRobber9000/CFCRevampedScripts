(async () => {
  var players = await bbgm.idb.cache.players.getAll();
  for (const p of players) {
    let age = bbgm.g.get("season")-p.born.year;
    if (age>=21 && bbgm.player.ovr(p.ratings.at(-1))>=80) {
      await bbgm.player.retire(p,{},{});
      await bbgm.idb.cache.players.put(p);
    }
  }
})();
