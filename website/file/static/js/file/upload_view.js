

class CustomDropZone extends DropZone {
}

;dz = new CustomDropZone()

dz.setup({
    dropSpace: '.single.drag-drop-zone'
    , formField: '#id_file'
    , clickThrough: true
});

const fileChangeHandler = function(e){
    let totalSize = 0;
    for(let file of e.target.files) {
        totalSize += file.size
    }

    console.log('size', sizeString(totalSize))

}

/**
 * Format bytes as human-readable text.
 *
 * @param bytes Number of bytes.
 * @param si True to use metric (SI) units, aka powers of 1000. False to use
 *           binary (IEC), aka powers of 1024.
 * @param dp Number of decimal places to display.
 *
 * @return Formatted string.
 */
function humanFileSize(bytes, si=false, dp=1) {
  const thresh = si ? 1000 : 1024;

  if (Math.abs(bytes) < thresh) {
    return bytes + ' B';
  }

  const units = si
    ? ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    : ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'];
  let u = -1;
  const r = 10**dp;

  do {
    bytes /= thresh;
    ++u;
  } while (Math.round(Math.abs(bytes) * r) / r >= thresh && u < units.length - 1);


  return bytes.toFixed(dp) + ' ' + units[u];
}


;document.querySelector('#id_file')
    .addEventListener('change', fileChangeHandler)
    ;