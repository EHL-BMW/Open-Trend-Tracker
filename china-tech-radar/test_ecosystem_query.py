import unittest

from scrape_china_tech_trends import TOPICS, topic_headline_relevant


class EcosystemQueryTest(unittest.TestCase):
    def test_query_covers_devices_accessories_and_ecodomain(self):
        query = next(topic[3] for topic in TOPICS if topic[0] == "phone_car_eco")
        for term in ("人车家", "生态域", "CarIoT", "车载生态配件", "智能生态配件", "车家互联", "HiCar", "NIO Link"):
            self.assertIn(term, query)
        self.assertNotIn('"HarmonyOS"', query)
        self.assertIn('"鸿蒙座舱"', query)

    def test_headline_filter_keeps_cross_device_news_without_generic_cockpit_news(self):
        relevant = (
            "上汽与OPPO发布汽车生态域，手机与车机共享能力",
            "小米汽车开放CarIoT车载生态配件",
            "蔚来NIO Link实现手机车机互联",
            "智能座舱与人车家生态横评",
            "小米汽车展示人车家全生态连接体验",
            "小米汽车开放智能生态配件接口",
            "车载应用跨端流转，手机与座舱无缝接续",
            "奕境X9首秀鸿蒙座舱6，多屏流转玩法公开",
            "鸿蒙座舱一碰就连，手机与车机无缝衔接",
        )
        unrelated = (
            "新车型搭载鸿蒙座舱与高阶智驾",
            "HarmonyOS手机发布会公布新平板",
            "智能家居IoT配件上新",
            "手机应用跨端流转到平板",
            "小米手机芯片发布，继续布局人车家全生态",
            "亚博ios版苹果版：开启智慧生活与车家互联新体验",
            "智能座舱和人车家生态横评：哪款更好+FAQ",
        )
        for title in relevant:
            with self.subTest(title=title):
                self.assertTrue(topic_headline_relevant("phone_car_eco", title))
        for title in unrelated:
            with self.subTest(title=title):
                self.assertFalse(topic_headline_relevant("phone_car_eco", title))


if __name__ == "__main__":
    unittest.main()
