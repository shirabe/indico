<%page args="tz=None"/>
<%
from indico.modules import ModuleHolder
from MaKaC.common.timezoneUtils import DisplayTZ
newsModule = ModuleHolder().getById("news")
newsList = newsModule.getNewsItemsList()
%>

<ul class="items">
    % for newItem in newsList[:2]:
        <li>
            <a class="title" href="${ urlHandlers.UHIndicoNews.getURL()}">
                ${ newItem.getTitle() }
            </a>
            <span class="timing">${ _('Posted on') }&nbsp;${ formatDate(newItem.getAdjustedCreationDate(tz)) }</span>
        </li>
    % endfor
</ul>
<div style="margin-top:10px; text-align: right;">
    <a href="${ urlHandlers.UHIndicoNews.getURL()}" class="subLink">${ _("View news history") }</a>
</div>
