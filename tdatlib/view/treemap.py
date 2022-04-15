from tdatlib.interface.treemap import frame as treemap_data
import plotly.graph_objects as go
import plotly.offline as of


class treemap(treemap_data):

    def __init__(self, category:str, sub_category:str=str(), kq:list=None):
        super().__init__(category=category, sub_category=sub_category, kq=kq)
        pass


    def view_map(self, key:str='R1D', save:bool or str=False):
        """
        :param key: 지도 표시 펙터
        :param save: 저장 여부
        :return:
        """
        frame = self.mapframe.copy()
        fig = go.Figure()
        unit = '%' if not key in ['PER', 'PBR'] else ''
        fig.add_trace(go.Treemap(
            ids=frame['ID'], labels=frame['종목명'], parents=frame['분류'], values=frame['크기'],
            marker=dict(colors=frame[f'C{key}']),
            textfont=dict(color='#ffffff'), textposition='middle center', texttemplate='%{label}<br>%{text}%<br>',
            meta=frame['시가총액'], customdata=frame['종가'], text=frame[key],
            branchvalues='total', opacity=0.9,
            hovertemplate='%{label}<br>시총: %{meta}<br>종가: %{customdata}<br>' + key + ': %{text}' + unit + '<extra></extra>'
        ))
        title = f'[{self.cat} / {self.mapname}]: {self.td_date} 종가 기준 {key}'
        fig.update_layout(title=title)
        if isinstance(save, bool) and save == True:
            of.plot(fig, filename=rf'./{self.cat}_{self.mapname}.html', auto_open=False)
        elif isinstance(save, str):
            of.plot(fig, filename=rf'{save}/{self.cat}_{self.mapname}.html', auto_open=False)
        else:
            fig.show()
        return

if __name__ == "__main__":
    tester = treemap(category='WICS')
    tester.view_map(save=True)