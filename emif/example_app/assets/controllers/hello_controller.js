import { Controller } from "stimulus"

export default class extends Controller {
  static targets = [ "name", "output" ]

  greet() {
    this.outputTarget.textContent =
      `Hello, ${this.nameTarget.value}!`
  }
}

// The HTML being backed by this controller could be:
// 
//   <div data-controller="hello">
//     <input data-target="hello.name" type="text">
//
//     <button data-action="click->hello#greet">
//       Greet
//     </button>
//
//     <span data-target="hello.output">
//     </span>
//   </div>
