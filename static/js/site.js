// Hero knobs (designer -> code sync demo) and the screenshot lightbox.
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function initKnob(el) {
    var min = parseFloat(el.dataset.min);
    var max = parseFloat(el.dataset.max);
    var step = parseFloat(el.dataset.step);
    var decimals = parseInt(el.dataset.decimals, 10);
    var unit = el.dataset.unit;
    var suffix = (unit.charAt(0) === ':' ? '' : ' ') + unit; // "4.0:1" but "-18.0 dB"
    var value = parseFloat(el.dataset.value);

    var arc = el.querySelector('[data-knob-arc]');
    var pointer = el.querySelector('[data-knob-pointer]');
    var readout = el.parentElement.querySelector('[data-knob-readout]');
    var line = document.getElementById(el.dataset.target);
    var codeValue = line && line.querySelector('[data-code-value]');
    var meter = el.dataset.intro !== undefined && document.querySelector('[data-meter]');

    function render(flash) {
      var pct = (value - min) / (max - min);
      var text = value.toFixed(decimals);
      arc.setAttribute('stroke-dasharray', (pct * 100).toFixed(1) + ' 100');
      pointer.setAttribute('transform', 'rotate(' + (-135 + 270 * pct).toFixed(1) + ' 36 36)');
      readout.textContent = text + suffix;
      el.setAttribute('aria-valuenow', text);
      el.setAttribute('aria-valuetext', text + suffix);
      if (codeValue) codeValue.textContent = text;
      // A lower threshold compresses harder, so the output meter drops.
      if (meter) meter.style.height = (35 + 55 * pct).toFixed(0) + '%';
      if (flash && line) {
        line.classList.remove('is-live');
        void line.offsetWidth; // restart the flash animation
        line.classList.add('is-live');
      }
    }

    function set(next) {
      next = Math.round(next / step) * step;
      next = Math.min(max, Math.max(min, next));
      if (next === value) return;
      value = next;
      render(true);
    }

    var dragStartY = 0;
    var dragStartValue = 0;
    el.addEventListener('pointerdown', function (e) {
      dragStartY = e.clientY;
      dragStartValue = value;
      el.setPointerCapture(e.pointerId);
      el.focus();
    });
    el.addEventListener('pointermove', function (e) {
      if (!el.hasPointerCapture(e.pointerId)) return;
      // 150px of vertical travel sweeps the full range.
      set(dragStartValue + (dragStartY - e.clientY) / 150 * (max - min));
    });
    el.addEventListener('keydown', function (e) {
      var big = (max - min) / 10;
      var delta = {
        ArrowUp: step, ArrowRight: step, ArrowDown: -step, ArrowLeft: -step,
        PageUp: big, PageDown: -big,
      }[e.key];
      if (e.key === 'Home') { set(min); e.preventDefault(); return; }
      if (e.key === 'End') { set(max); e.preventDefault(); return; }
      if (delta === undefined) return;
      e.preventDefault();
      set(value + delta);
    });

    // One intro sweep on load so visitors see the link between knob and code.
    if (el.dataset.intro !== undefined && !reduceMotion) {
      var target = value;
      var from = parseFloat(el.dataset.intro);
      var start = null;
      var duration = 1400;
      value = from;
      render(false);
      setTimeout(function () {
        requestAnimationFrame(function tick(now) {
          if (start === null) start = now;
          var t = Math.min(1, (now - start) / duration);
          var eased = 1 - Math.pow(1 - t, 3);
          value = Math.round((from + (target - from) * eased) / step) * step;
          render(t === 1);
          if (t < 1) requestAnimationFrame(tick);
        });
      }, 600);
    } else {
      render(false);
    }
  }

  function initLightbox(dialog) {
    var img = dialog.querySelector('img');
    var caption = dialog.querySelector('figcaption');
    document.querySelectorAll('[data-lightbox]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        img.src = btn.dataset.full;
        img.alt = btn.dataset.caption || '';
        caption.textContent = btn.dataset.caption || '';
        caption.hidden = !btn.dataset.caption;
        dialog.showModal();
      });
    });
    dialog.addEventListener('click', function (e) {
      // Clicks on the backdrop land on the dialog element itself.
      if (e.target === dialog) dialog.close();
    });
    dialog.addEventListener('close', function () { img.removeAttribute('src'); });
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-knob]').forEach(initKnob);
    var dialog = document.getElementById('lightbox');
    if (dialog) initLightbox(dialog);
  });
})();
