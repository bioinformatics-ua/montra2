const Utils = {

    addClass: function(element, theClass) {
      element.classList.add(theClass);
    },
  
    removeClass: function(element, theClass) {
      element.classList.remove(theClass);
    },
  
    showMore: function(element, excerpt) {
      element.addEventListener("click", event => {
        const linkText = event.target.textContent.toLowerCase();
        event.preventDefault();

        var init_height = excerpt.offsetHeight;

        if (element.parentElement.classList.contains('opentext-large')){
          if (linkText == "show more") {
            element.textContent = "Show less";
            this.removeClass(excerpt, "large-text");
          } else {
            element.textContent = "Show more";
            this.addClass(excerpt, "large-text");
          }
        } else if (element.parentElement.classList.contains('opentext-mid')){
          if (linkText == "show more") {
            element.textContent = "Show less";
            this.removeClass(excerpt, "mid-text");
          } else {
            element.textContent = "Show more";
            this.addClass(excerpt, "mid-text");
          }
        } else if (element.parentElement.classList.contains('opentext-list')) {
          if (linkText == "show more") {
            element.textContent = "Show less";
            this.removeClass(excerpt, "list-text");
          } else {
            element.textContent = "Show more";
            this.addClass(excerpt, "list-text");
          }
        }

        cardBodies = document.querySelectorAll('.card-pf-body');

        const variance = excerpt.offsetHeight - init_height;

        cardBodies.forEach(function (elem) { elem.style.height = elem.offsetHeight + variance + 'px'; })
  
      });
    } 
  };
  
  const ExcerptWidget = {
    showMore: function(showMoreLinksTarget, excerptTarget) {

      const showMoreLinks = document.querySelectorAll(showMoreLinksTarget);

      showMoreLinks.forEach(function(link) {
        //First check if text will overflow in width or height
        const excerpt = link.previousElementSibling;
        var curOverflow = excerpt.style.overflow;

        if ( !curOverflow || curOverflow === "visible" )
           excerpt.style.overflow = "hidden";
     
        var isOverflowing = excerpt.clientWidth < excerpt.scrollWidth 
           || excerpt.clientHeight < excerpt.scrollHeight;
     
        excerpt.style.overflow = curOverflow;
        if (!isOverflowing) {
          link.parentNode.classList.remove("expandable-text")
          link.parentNode.removeChild(link);
        }

        Utils.showMore(link, excerpt);
      });

  }
};

ExcerptWidget.showMore('.js-show-more');