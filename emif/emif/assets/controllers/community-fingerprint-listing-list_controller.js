import { Controller } from "stimulus"

export default class extends Controller {
  static targets = [ 
              'resultsTable'
            ]

  /*====================================*/
  /*  Lifecycle methods                 */
  /*====================================*/

  connect() {

  }

  /*====================================*/
  /*  Public methods                    */
  /*====================================*/

  onSelect(event){
    var element = event.currentTarget;
    if ($(element).is(":checked")) {
      $(element).closest('.list-group-item').addClass("active-line");
    } else {
        $(element).closest('.list-group-item').removeClass("active-line");
    }
  }

  /*====================================*/
  /*  Private methods                   */
  /*====================================*/


}