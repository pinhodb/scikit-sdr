import ipywidgets as widgets
#from IPython.display import Javascript, display

description_width_style = {'description_width': 'initial'}

def header_widget(title):
    header = widgets.HTML('<h1 align="center">' + title + '</h1>', layout=widgets.Layout(height='auto'))
    header.style.text_align = 'center'
    return header

def disable_scroll_output_widgets():
    # Hack to disable scrolling in output widgets
    style = """
        <style>
        .jupyter-widgets-output-area .output_scroll {
                height: unset !important;
                border-radius: unset !important;
                -webkit-box-shadow: unset !important;
                box-shadow: unset !important;
            }
            .jupyter-widgets-output-area  {
                height: auto !important;
            }
        </style>
    """
    return widgets.HTML(style)

def disable_scroll():
    disable_scroll_js = """
        IPython.OutputArea.prototype._should_scroll = function(lines) {
            return false;
        }
    """
    return Javascript(disable_scroll_js)

def display_hacks():
    display(disable_scroll_output_widgets())
    display(disable_scroll())
    pass
