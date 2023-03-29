
$(function(){
    $(document).on('change', '.btn-file :file', function() {
      var input = $(this),
          numFiles = input.get(0).files ? input.get(0).files.length : 1,
          label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
      input.trigger('fileselect', [numFiles, label]);
    });

    $('.btn-file :file').on('fileselect', function(event, numFiles, label) {

        var input = $(this).parents('.input-group').find(':text'),
            log = numFiles > 1 ? numFiles + ' files selected' : label;

        if( input.length ) {
            input.val(log);
        } else {
            if( log ) alert(log);
        }

    });

    var editor = new wysihtml5.Editor("editor", { // id of textarea element
      toolbar:      "wysihtml5-toolbar", // id of toolbar element
      parserRules:  wysihtml5ParserRules, // defined in parser rules set
      stylesheets: [$('#base_link').attr('href')+"static/css/vendor/wysihtml5.css"],

    });
    var editor_short = new wysihtml5.Editor("editor_short", { // id of textarea element
      toolbar:      "wysihtml5-toolbar-short", // id of toolbar element
      parserRules:  wysihtml5ParserRules, // defined in parser rules set
      stylesheets: [$('#base_link').attr('href')+"static/css/vendor/wysihtml5.css"],

    });

    $('#tag_container').tagsinput({
      tagClass: 'label label-primary',
      typeahead: {
        source: function(query) {
          return $.get($('#base_link').attr('href')+'tag/autocomplete/'+query);
        },
        displayText: function(item){
          return item;
        }
      }
    });


    // Icons and Thumbnails. 

    function IconThumbnailComponent() {

      this.vanillaIcon = document.querySelector('.community_icon');
      this.vanillaThumbnail = document.querySelector('.community_thumbnail');
      this.vanillaPreview = document.querySelector('.image_preview');

      this.communityIcon = undefined;
      this.communityThumbnail = undefined;
      this.oldvw = undefined;

      this.MAX_ICON_HEIGHT = 103;
      this.MAX_ICON_WIDTH = 500;
      this.MAX_THUMB_SIZE = 150;
      this.MAX_SIZE = 600;

    };
    IconThumbnailComponent.prototype.init = function() {
        var self = this;
        self.initialize(self.MAX_THUMB_SIZE,self.MAX_THUMB_SIZE,self.MAX_SIZE,self.MAX_SIZE);
        self.initialize(self.MAX_ICON_WIDTH,self.MAX_ICON_HEIGHT,self.MAX_SIZE,self.MAX_SIZE);
        

        self.vanillaIcon.addEventListener('click', function() {
          self.initialize(self.MAX_ICON_WIDTH,self.MAX_ICON_HEIGHT,self.MAX_SIZE,self.MAX_SIZE);
        });
        self.vanillaThumbnail.addEventListener('click', function() {
          self.initialize(self.MAX_THUMB_SIZE,self.MAX_THUMB_SIZE,self.MAX_SIZE,self.MAX_SIZE);
        });
        self.vanillaPreview.addEventListener('click', function() {
          self.vanilla.result('canvas').then(self.resultVanilla.bind(self));
        });
    };

    IconThumbnailComponent.prototype.initialize = function(vw,vh,bw,bh) {
      var self = this;
      if(self.oldvw!=undefined && self.oldvw!=vw){
        if(vw!=self.MAX_ICON_WIDTH) self.vanilla.result('canvas').then(
          function(result){
            self.communityThumbnail=result; 
            $("#thumbnail").val(self.communityThumbnail);
          }
        );
        else 
          self.vanilla.result('canvas').then(
            function(result){
              self.communityIcon=result; 
              $("#icon").val(self.communityIcon);
            }
        );
      }
      $('#vanilla-demo').empty();
      self.vanilla = new Croppie(document.getElementById('vanilla-demo'), {
        viewport: {
          width: vw,
          height: vh
        },
        boundary: {
          width: bw,
          height: bh
        },
        
        enableOrientation: true
      });
      self.vanilla.bind({
        url: comm_icon_url,
        orientation: 1,
        enforceBoundary: false,
        mouseWheelZoom: true,
        zoom: 1
      });
      self.oldvw = vw;
    };

    IconThumbnailComponent.prototype.resultVanilla = function(result) {
      var self = this;
      console.log("oldvw: " + self.oldvw);
      
      // Load Previous values. 
      if(self.oldvw==self.MAX_ICON_WIDTH) {self.communityIcon=result; $("#icon").val(self.communityIcon); }
      if(self.oldvw==self.MAX_THUMB_SIZE) {self.communityThumbnail=result; $("#thumbnail").val(self.communityThumbnail); }

      // FIXME !! 
      var url = "";
      
      // Thumbnail 
      if (self.communityThumbnail!==undefined){
        var base64ImageContentThumb = self.communityThumbnail.replace(/^data:image\/(png|jpg);base64,/, "");
        var blobThumb = base64ToBlob(base64ImageContentThumb, 'image/png');
      }
      
      // Icon 

      if (self.communityIcon!==undefined){
        var base64ImageContentIcon = self.communityIcon.replace(/^data:image\/(png|jpg);base64,/, "");
        var blobIcon = base64ToBlob(base64ImageContentIcon, 'image/png');
      }
      

      var formData = new FormData();

      formData.append('new_logo', blobIcon);
      formData.append('new_thumb', blobThumb);

      $.ajax({
          url: url, 
          type: "POST", 
          cache: false,
          contentType: false,
          processData: false,
          data: formData})
              .done(function(e){
                  // TODO: fix me here
                  // alert('done!');
              });  
      
      var message = ""

      if (self.communityThumbnail) {
        message = message.concat('<p>Community thumbnail <br><img src="' + self.communityThumbnail + '" /></p>')
      }
      if (self.communityIcon) {
        message = message.concat('<p>Community icon <br><img src="' + self.communityIcon + '" /></p>')
      }

      var bd = bootbox.dialog({
          title: 'Community Logo - saved with success',
          message: message,
          buttons: {
              success: {
                  label: "Close",
                  className: "btn",
                  callback: function() {
                      var name = $('#gname').val();

                      if(name && name.length > 0){
                          $('#gadd').val(name);
                          bd.modal('hide');
                          $('#gname_add').submit();

                      }

                  }
              }
          }
      });
    };

    var iconComponents = new IconThumbnailComponent();
    iconComponents.init();

    // Auxiliar method to convert image to 
    function base64ToBlob(base64, mime) 
    {
        mime = mime || '';
        var sliceSize = 1024;
        var byteChars = window.atob(base64);
        var byteArrays = [];

        for (var offset = 0, len = byteChars.length; offset < len; offset += sliceSize) {
            var slice = byteChars.slice(offset, offset + sliceSize);

            var byteNumbers = new Array(slice.length);
            for (var i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }

            var byteArray = new Uint8Array(byteNumbers);

            byteArrays.push(byteArray);
        }

        return new Blob(byteArrays, {type: mime});
    }

});
