const template = /*__DOCUMENT__*/;

export default function(component) {
  const {parentElement, data} = component;
  let frame = parentElement.querySelector('iframe');
  if (!frame) {
    frame = document.createElement('iframe');
    frame.dataset.instance = crypto.randomUUID();
    frame.title = 'AquaControl: estanque, sensores y actuadores';
    frame.style.cssText = 'display:block;width:100%;height:1000px;border:0;';
    frame.setAttribute('sandbox', 'allow-scripts allow-same-origin');
    // Data is JSON, never executable markup. Escape script terminators.
    const payload = JSON.stringify(data).replace(/</g, '\\u003c').replace(/>/g, '\\u003e').replace(/&/g, '\\u0026');
    frame.srcdoc = template.replace('__SNAPSHOT_JSON__', payload);
    parentElement.appendChild(frame);
  }
  frame.aquaSnapshot = data;
  const send = () => frame.contentWindow?.postMessage({type:'aquacontrol:snapshot',snapshot:frame.aquaSnapshot}, '*');
  frame.onload = send;
  send();
}
