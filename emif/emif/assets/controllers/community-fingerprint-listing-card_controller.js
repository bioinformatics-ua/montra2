import { Controller } from "stimulus";

export default class extends Controller {
  static targets = ["resultsTable"];

  /*====================================*/
  /*  Lifecycle methods                 */
  /*====================================*/

  connect() {
    $(".row-cards-pf > [class*='col'] > .card-pf > .card-pf-body").matchHeight();
  }

  /*====================================*/
  /*  Public methods                    */
  /*====================================*/

  onSelect(event) {
    var element = event.currentTarget;
    if (
      $(element)
        .parent()
        .parent()
        .hasClass("active-line")
    ) {
      $(element)
        .parent()
        .parent()
        .removeClass("active-line");
    } else {
      $(element)
        .parent()
        .parent()
        .addClass("active-line");
    }
  }

  /*====================================*/
  /*  Private methods                   */
  /*====================================*/
}
