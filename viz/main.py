#!/usr/bin/env python
# coding: utf-8

# In[166]:


# %reset


# In[2]:


# REFERENCE 

# Bokeh Plotting: Enable tooltips for only some glyphs
# https://stackoverflow.com/questions/29435200/bokeh-plotting-enable-tooltips-for-only-some-glyphs

# Bokeh Documentation: Configuring Plot Tools
# https://docs.bokeh.org/en/latest/docs/user_guide/tools.html

# Bokeh Documentation: Styling Visual Attributes
# https://docs.bokeh.org/en/latest/docs/user_guide/styling.html


# In[3]:


import pandas as pd 
import os

from bokeh.io import output_notebook, show, curdoc
from bokeh.plotting import figure
from bokeh.layouts import column, gridplot
from bokeh.models import ColumnDataSource, TapTool, OpenURL, CustomJSHover, Circle, Line, Text
from bokeh.models.tickers import DatetimeTicker
from bokeh.models.tools import HoverTool, PanTool, BoxZoomTool, WheelZoomTool, SaveTool, ResetTool, TapTool

# from sklearn.preprocessing import MinMaxScaler


# In[9]:


fileName = './viz/200927_ParsedVideoData_v4.csv'
print(os.getcwd())
data = pd.read_csv(fileName)

data.publishedAt = pd.to_datetime(data.publishedAt)
data.duration = pd.to_timedelta(data.duration)


# In[10]:


dataColor1 = '#003f5c'
dataColor2 = '#7a5195'
dataColor3 = '#ef5675'
dataColor4 = '#ffa600'


# In[11]:


# normalize data for plotting
data_columns = ['viewCount', 'likeCount', 'dislikeCount', 'commentCount']
source_columns = [x +'Norm' for x in data_columns]
# data_normalized = pd.DataFrame(MinMaxScaler().fit_transform(data[data_columns]), columns=source_columns)
data_normalized =(data[data_columns] -  data[data_columns].min())/(data[data_columns].max() - data[data_columns].min())
data_normalized.columns = source_columns
data = pd.concat([data, data_normalized], axis=1)


# In[13]:


source = ColumnDataSource(data)

data_colors = [dataColor3, dataColor4, dataColor1, dataColor2]

# url to open on click
url = 'https://www.youtube.com/watch?v=@id'

# configure hover tooltips
hover_data = [('Guest', '@guestName'),
             ('Number', '@videoNumber{0,0}'),
             ('Aired On', '@publishedAt{%F}'),
             ('View', '@viewCount{0,0.0 a}'),
             ('Likes', '@likeCount{0,0.0 a}'),
             ('Dislikes', '@dislikeCount{0,0.0 a}'),
             ('Comments', '@commentCount{0,0.0 a}'),
            ]

figure_titles = ['Views', 'Likes', 'Dislikes', 'Comments']
figure_collector = []

# add title 
fig_title = 'The Joe Rogan Experience YouTube Statistics (2013 - 2020)'
sub_title = 'Hover over line peak to see video details. Click to open YouTube video in new tab.'

def create_text(text, text_color='grey', text_font_size='20px', fig_len=1200, fig_height=130):
    fig = figure(plot_width=fig_len, plot_height=fig_height)
    text = Text(x=data['publishedAt'].min(), y=0,                      text=[text], text_color=text_color, text_font_size=text_font_size)
    fig.add_glyph(text)
     # decrease clutter
    fig.outline_line_color = None
    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_color = None
    fig.yaxis.visible = False
    fig.xaxis.visible = False 
    return fig
    
def create_figures(source, source_columns, fig_len=1400, fig_height=120, data_colors=data_colors, hover_data=hover_data, alpha=0.,
                   figure_collector=figure_collector, fig_title=fig_title, sub_title=sub_title):

    
    # title = create_text(fig_title, text_color='#2b2d2f', text_font_size='40px', fig_height=60)
    # sub_title = create_text(sub_title, text_color='grey', text_font_size='20px', fig_height=40)
    # figure_collector.append(title)
    # figure_collector.append(sub_title)

   
    num_figures = len(source_columns)
    num = 0
    

    while num < num_figures:
        # create figure
        fig = figure(plot_width=fig_len, plot_height=fig_height, x_axis_type='datetime', name='data_series', output_backend="webgl")

        # add tools
        tools = [PanTool(), BoxZoomTool(), WheelZoomTool(), SaveTool(), ResetTool()]
        fig.add_tools(*tools)
        
        # create the scatter plot 
        scatter = Circle(x='publishedAt', y=source_columns[num], line_color=data_colors[num], fill_color=data_colors[num],                          size=6, fill_alpha=alpha, line_alpha=alpha
                        )
        scatter_render = fig.add_glyph(source_or_glyph=source, glyph=scatter)
        # hover only over scatter plot
        hover = HoverTool(renderers=[scatter_render], tooltips=hover_data, formatters={'@publishedAt':'datetime'})
        fig.add_tools(hover)
        # open video url on tap scatter points
        taptool = TapTool(renderers=[scatter_render])
        taptool.callback = OpenURL(url=url)
        fig.add_tools(taptool)
    
        # create line plot without hover or top 
        line = Line(x='publishedAt', y=source_columns[num], line_color=data_colors[num], line_width=2, line_alpha=1)
        line_render = fig.add_glyph(source_or_glyph=source, glyph=line)
        
        # add series title
        title = Text(x=data['publishedAt'].min(), y=0.2,                      text=[figure_titles[num]], text_color=data_colors[num], text_font_size='35px')
        fig.add_glyph(title)
                
        # decrease clutter
        fig.outline_line_color = None
        fig.xgrid.grid_line_color = None
        fig.ygrid.grid_line_color = None
        fig.yaxis.visible = False
        fig.xaxis.visible = False   
        
        
        # format x-axis ticks 
        fig.xaxis.major_tick_line_color = "grey"
        fig.xaxis.major_label_text_font_size = "15pt"
        fig.xaxis.major_label_text_color = "grey"

        
        # collect figures in a list 
        figure_collector.append(fig)
        num+=1
    return figure_collector

figures = create_figures(source, source_columns)

# show x-axis on the bottom figure
figures[-1].xaxis.visible = True
figures[-1].xaxis.ticker = DatetimeTicker(desired_num_ticks=10)
figures[-1].xaxis.axis_line_color = 'grey'



# # share last figures x-axis with all figures to allow linked zoom and pan
for fig in figures[:-1]: 
    fig.x_range = figures[-1].x_range
    fig.y_range = figures[-1].y_range


layout = gridplot(figures, ncols=1)
curdoc().add_root(layout)
curdoc().title = 'JRE Data Visualization'

# uncomment if viewing on Jupyter Notebook
# output_notebook()
# show(layout)


# In[ ]:




