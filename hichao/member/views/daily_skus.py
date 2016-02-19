# -*- coding:utf-8 -*-

from hichao.util.statsd_client import statsd
from pyramid.view import (
        view_defaults,
        view_config,
        )
from pyramid.response import Response
from hichao.base.views.view_base import View
from hichao.app.views.oauth2 import check_permission
from hichao.util.pack_data import pack_data, version_ge
from hichao.user.models.user import get_user_by_id
from hichao.shop.models.user import get_ec_user_by_user_id
from hichao.shop.models.order_info import get_user_amount_paid
from hichao.shop.models.goods_member import get_all_goods
from hichao.shop.models.business_discount import get_discounts_by_business_id
from hichao.shop.models.goods import get_goods_by_goods_id
from hichao.shop.models.goods_source import get_source_id_by_goods_id
from hichao.member.config import (
        RANK_MONEY,
        MAX_RANK,
        )
import json
from hichao.sku.models.sku import get_sku_from_icehole_by_source_id

@view_defaults(route_name = 'member_daily_skus')
class DailySkusView(View):
    def __init__(self, request):
        super(DailySkusView, self).__init__()
        self.request = request

    @statsd.timer("hichao_backend.r_member_daily_skus.get")
    @check_permission
    @view_config(request_method = 'GET', renderer = 'member/daily_skus.html')
    @pack_data
    def get(self):
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        if self.user_id < 1:
            app_api = self.request.params.get('ga', '')
            res = {}
            res['error'] = 'user is not login.'
            res['errorCode'] = '20001'
            res['message'] = ''
            res['data'] = {}
            res['data']['appApi'] = app_api
            return Response(json.dumps(res), content_type = 'application/json')
        user = {}
        skus = []
        user_info = get_user_by_id(self.user_id)
        user_rank_info = get_ec_user_by_user_id(self.user_id)

        user['username'] = user_info.get_component_user_name()
        user['userAvatar'] = user_info.get_component_user_avatar()

        rank = user_rank_info.get_rank() if user_rank_info else 0
        rank_str = user_rank_info.get_component_user_rank() if user_rank_info else 'v0'
        next_rank = user_rank_info.get_next_rank() if user_rank_info else 0
        next_rank_str = user_rank_info.get_component_user_next_rank() if user_rank_info else 'v1'
        total_paid = float(user_rank_info.get_component_user_money()) if user_rank_info else 0
        user_has_demoted = user_rank_info.has_demoted() if user_rank_info else 0
        if rank < MAX_RANK:
            need_paid_next_rank = RANK_MONEY[rank + 1] - total_paid
            rank_rate = (total_paid - RANK_MONEY[rank])/float(RANK_MONEY[rank + 1] - RANK_MONEY[rank])
            rank_rate = '{0}%'.format(rank_rate * 100)
            if user_has_demoted:
                rank_rate = '95%'
        else:
            need_paid_next_rank = 0
            rank_rate = '100%'

        user['rank'] = rank
        user['rankStr'] = rank_str
        user['nextRank'] = next_rank
        user['nextRankStr'] = next_rank_str
        user['needPaidNextRank'] = need_paid_next_rank
        user['totalPaid'] = total_paid
        user['rankRate'] = rank_rate
        user['hasDemoted'] = user_has_demoted

        goods = get_all_goods()
        for _goods in goods:
            sku = {}
            discounts = get_discounts_by_business_id(_goods.get_component_business_id())
            discount = discounts.get(rank, '')
            if not discount:
                discount_ranks = sorted(discounts.keys())
                for r in discount_ranks:
                    if r > rank: break
                    discount = discounts[r]
            if not discount: discount = 1
            goods_price_info = get_goods_by_goods_id(_goods.get_component_goods_id())
            source_id = get_source_id_by_goods_id(_goods.get_component_goods_id())
            sku['picUrl'] = _goods.get_component_pic_url()
            sku['originPrice'] = goods_price_info.get_component_price()
            sku_source = get_sku_from_icehole_by_source_id(source_id)
            if sku_source:
                sku['originPrice'] = sku_source.curr_price
            sku['discountPrice'] = goods_price_info.get_component_discount_price(discount)
            sku['discountPrice'] = format(float(sku['originPrice']) * float(discount), '.2f')
            sku['stateMessage'] = goods_price_info.get_goods_state_msg()
            if rank > 1:
                low_discount = 1
                for x in range(0, rank):
                    if discounts.get(x, ''): low_discount = discounts[x]
                sku['lowRankDiscountPrice'] = goods_price_info.get_component_discount_price(low_discount)
            sku['title'] = _goods.get_component_title()
            sku['discount'] = '{0}折'.format(discount * 10, '.2')
            action = {}
            action['actionType'] = 'detail'
            action['type'] = 'sku'
            action['source'] = 'ecshop'
            if source_id:
                action['sourceId'] = str(source_id)
            else:
                action['goodsId'] = _goods.get_component_goods_id()
            if (gf == 'iphone' and version_ge(gv, '6.3.4')) or (gf == 'android' and version_ge(gv, 634)):
                sku['action'] = action
            else:
                sku['action'] = json.dumps(action)
            skus.append(sku)
        if (gf == 'iphone' and version_ge(gv, '6.3.4')) or (gf == 'android' and version_ge(gv, 634)):
            if user['hasDemoted']:
                remind = '根据保级规则，您在同一自然季度内消费满300元，恢复{0}级别。\n(付款生效15天后金额计入)'.format(user['nextRankStr'])
            else:
                if user['rank'] == 0:
                    remind = '在商城消费一次即可升入V1级别\n(付款生效15天后金额计入)'
                elif user['rank'] < 4:
                    remind = '您已累计消费{0}元\n再消费{1}元即可升入{2}级别\n(付款生效15天后金额计入)'.format(
                        user['totalPaid'],user['needPaidNextRank'],user['nextRankStr'])
                else:
                    remind = '您已累计消费{0}元\n已达到最高级别'.format(user['totalPaid'])
            user['rankInformation'] = remind
            data = {}
            data['data'] = {}
            data['message'] = ''
            data['data']['user'] = user
            data['data']['skus'] = skus
            return Response(json.dumps(data), content_type = 'application/json')
        return '', {'user':user, 'skus':skus}

