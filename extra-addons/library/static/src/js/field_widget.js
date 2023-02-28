odoo.define('my_field_widget', function (require) {
    "use strict";
    
    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');

    // importando o qweb
    var core = require('web.core');
    var qweb = core.qweb;
    
    // criando o wedget por meio da var AbstractField
    var colorField = AbstractField.extend({
       //nome da class, tag do elemento e os tipo do campo
        className: 'o_int_colorpicker',
        tagName: 'span',
        supportedFieldTypes: ['integer'],
        
        // eventos JS
        events: {
            'click .o_color_pill': 'clickPill',
        },

        // faze algumas alterações no init
        init: function () {
            this.totalColors = 10;
            this._super.apply(this, arguments);
        },

        //configurar os elementos DOM
        // _renderEdit: function () {
        //     this.$el.empty();
        //     var pills = qweb.render('FieldColorPills', {widget: this});
        //     this.$el.append(pills);
        // },
        _renderEdit: function () {
            this.$el.empty();
            for (var i = 0; i < this.totalColors; i++ ) {
                var className = "o_color_pill o_color_" + i;
                if (this.value === i ) {
                    className += ' active';
                }
                this.$el.append($('<span>', {
                    'class': className,
                    'data-val': i,
                }));
            }
        },
        _renderReadonly: function () {
            var className = "o_color_pill active readonly o_color_" + this.value;
            this.$el.append($('<span>', {
                'class': className,
            }));
        },

        // difinir os manipuladores
        clickPill: function (ev) {
            var $target = $(ev.currentTarget);
            var data = $target.data();
            this._setValue(data.val.toString());
        }
    
    });
    
    //registra o widget
    fieldRegistry.add('int_color', colorField);
    
    //disponibilizar para os outros
    return {
        colorField: colorField,
    };
    });