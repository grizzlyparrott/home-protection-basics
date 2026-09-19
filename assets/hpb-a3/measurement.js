/* Uses the existing GA4 gtag implementation; no new analytics architecture. */
(function () {
  function send(name, parameters) {
    if (typeof window.gtag === 'function') window.gtag('event', name, parameters);
  }

  document.addEventListener('click', function (event) {
    var printButton = event.target.closest('[data-hpb-print]');
    if (printButton) {
      send('hpb_checklist_print', { content_group: 'power_outage', page_path: window.location.pathname });
      window.print();
      return;
    }
    var link = event.target.closest('article a[href]');
    if (!link) return;
    var isSource = Boolean(link.closest('[aria-labelledby="sources"]')) && link.hostname !== window.location.hostname;
    var isRelated = Boolean(link.closest('.hpb-related-links')) && link.hostname === window.location.hostname;
    if (isSource) {
      send('hpb_source_open', { content_group: 'a3_priority', page_path: window.location.pathname, link_url: link.href });
    } else if (isRelated) {
      send('hpb_cluster_navigation', { content_group: 'a3_priority', page_path: window.location.pathname, destination_path: link.pathname });
    }
  });
}());
