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
        $(element).closest('.table-row').addClass("active-line");
    } else {
        $(element).closest('.table-row').removeClass("active-line");
    }
  }

  /*====================================*/
  /*  Private methods                   */
  /*====================================*/


}