document.addEventListener('DOMContentLoaded', function () {
  const modal = document.getElementById('image-modal');
  const modalImage = document.getElementById('modal-image');
  const modalTitle = document.getElementById('modal-title');
  const modalClose = document.getElementById('modal-close');
  const modalAction = document.getElementById('modal-action');

  function openModal(src, title) {
    modalImage.src = src;
    modalImage.alt = title;
    modalTitle.textContent = title;
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
  }

  function closeModal() {
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden', 'true');
    modalImage.src = '';
    modalTitle.textContent = '';
  }

  document.querySelectorAll('.image-open').forEach(function (el) {
    el.addEventListener('click', function (ev) {
      ev.preventDefault();
      const src = el.getAttribute('data-image');
      const title = el.getAttribute('data-title') || '';
      openModal(src, title);
    });
  });

  modalClose?.addEventListener('click', function () {
    closeModal();
  });

  modal?.addEventListener('click', function (ev) {
    if (ev.target === modal) closeModal();
  });

  modalAction?.addEventListener('click', function () {
    const title = modalTitle.textContent;
    alert('To add "' + title + '" to cart, open the product page and add from there.');
  });
});
