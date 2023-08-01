function checkPersistence(callback) {
  if (typeof (window.Persistence) !== 'undefined' && Persistence.isAvailable()) {
    callback();
  } else {
    document.getElementById('root').innerHTML =
      '<div class="big-red">Sorry but this card cannot be ' +
      "displayed on this Anki client.</div>" +
      "<br/>" +
      "<div>This card cannot be previsualized in some platforms. " +
      "Make sure it actually works at study time.</div>" +
      "<br/>" +
      "<div>Please, contact the developer of the deck to let " +
      "them know something went wrong :)</div>";
  }
}

function getChunks(fun, clean = true) {

  var chunks = fun.toString()
    //Strip HTML
    .replace(/<div>/g, "\n")
    .replace(/<\/div>/g, "\n")
    .replace(/<\/?br ?\/?>/g, "\n");

  if (clean) {
    chunks = chunks
      .replace(/\s*</g, "<")
      .replace(/>\s*/g, ">")
  }

  chunks = chunks.split('EOL');
  chunks = chunks.slice(1, chunks.length - 1);
  return chunks;
}

function shuffle(array) {
  var i = array.length, tmpVal, rnd;
  // While there remain elements to shuffle...
  while (0 !== i) {
    // Pick a remaining element...
    rnd = Math.floor(Math.random() * i);
    i -= 1;
    // And swap it with the current element.
    tmpVal = array[i];
    array[i] = array[rnd];
    array[rnd] = tmpVal;
  }
  return array;
}

function playAudio(id) {
  var query = ['', ' > .replaybutton', ' > [title="Replay"]', ' > a']
    .map(q => '#' + id.toString() + q)
    .join(', ');
  var links = document.querySelectorAll(query);
  for (var link of links) {
    if (link instanceof HTMLAnchorElement) {
      link.click();
      break;
    }
  }
}
