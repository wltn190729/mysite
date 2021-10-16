import json
import os
import re
from pprint import pprint

import requests
from django.test import TestCase
from bs4 import BeautifulSoup
from mysite.settings import STATIC_DIR
from difflib import SequenceMatcher


class TestClass(TestCase):

    # noinspection PyMethodMayBeStatic
    # 2차원 리스트에서 중복된 값을 제거하고 중복된 개수를 반환하는 함수
    def getDupCount(self, attr_list):
        dup_list = []
        dup_count = []

        # id 값 모두 추출하는 루프문
        id_list = []
        for i in attr_list:
            for j in i:
                if j[0] == "id":
                    id_list.append(j[1][0])

        for i in attr_list:
            for j in i:
                if j[0] == "id":
                    for similar_id in self.getSimilar_id(id_list):
                        if similar_id in j[1][0]:
                            j[1][0] = similar_id

        for i in self.getCombinations(attr_list, 2):
            for j in i[0]:  # 1번째 j ['class', ['name']
                for k in i[1]:  # 2번째 k ['class', ['name']
                    if j[0] == k[0] and (
                            j[0] == "class" or j[0] == "id"):  # j[0] -> 속성, k[0] -> 속성, j[1] -> 내용, k[1] -> 내용
                        if list(set(j[1]).intersection(k[1])):
                            dup_list.append([j[0], list(set(j[1]).intersection(k[1]))])

        for i in dup_list:
            count = dup_list.count(i)
            if [i, count] not in dup_count:
                dup_count.append([i, count])

        return dup_count

    # noinspection PyMethodMayBeStatic
    # 두개의 스트링의 중복되는 스트링의 일부분과 유사성을 리턴하는 함수
    def getSimilar_compare(self, str_list):
        similar_list = []

        for i in self.getCombinations(str_list, 2):
            if len(i[0]) <= len(i[1]):
                str_small, str_large = i[0], i[1]
            else:
                str_small, str_large = i[1], i[0]

            max_length = 0
            max_result = ''
            for i in self.getCombinations(list(range(len(list(str_small)))), 2):
                word = "".join([str_small[j] for j in range(i[0], i[1] + 1)])
                if word in str_large:
                    if len(word) > max_length:
                        max_length = len(word)
                        max_result = word

            ratio = SequenceMatcher(None, max_result, str_large).ratio()

            similar_list.append({'result': max_result, 'ratio': ratio})

        return similar_list

    # noinspection PyMethodMayBeStatic
    # id 값을 담은 리스트에서 비슷한 id 라고 추정되는 것을 추출 후 다시 id 담은 리스트에 담아주는 함수 (코드 간결화 필요)
    def getSimilar_id(self, id_list):
        id_list_origin = id_list
        compare_result = []

        for i in range(2):
            id_list_2 = []
            for j in self.getSimilar_compare(id_list):
                if j['ratio'] > 0.8:
                    id_list_2.append(j['result'])
                    if not compare_result:
                        compare_result = id_list_2
                    else:
                        for k in compare_result:
                            if j['result'] in k:
                                compare_result.remove(k)
            id_list = id_list_2
        remove_list = []
        for i in compare_result:
            for j in id_list_origin:
                if i in j:
                    if SequenceMatcher(None, i, j).ratio() > 0.8:
                        remove_list.append(j)

        result_list = compare_result + list(set(id_list_origin).difference(remove_list))

        return result_list

    # 조합함수 (Combinations Function)
    def getCombinations(self, arr, r):
        for i in range(len(arr)):
            if r == 1:  # 종료 조건
                yield [arr[i]]
            else:
                for next in self.getCombinations(arr[i + 1:], r - 1):
                    yield [arr[i]] + next

    # noinspection PyMethodMayBeStatic
    # 1차원 리스트를 순서 유지한 채로 중복 없이 만드는 함수
    def getListNoneDuple(self, list):
        new_list = []
        for v in list:
            if v not in new_list:
                new_list.append(v)

        return new_list

    # noinspection PyMethodMayBeStatic
    # plaintext 를 포함한 상위태그들의 id 나 class 값을 리스트 형태로 리턴하는 함수
    def getPlainParent(self, soup, plain_list):
        plain_attr_lists = []

        for plain in plain_list:
            plain_attr_list_one = []
            for tag in soup.findAll(lambda tag: tag.get_text().find(plain) != -1)[::-1]:
                for tag_attr in tag.attrs.items():
                    tag_attr = list(tag_attr)
                    if tag_attr[0] == "id":
                        tag_attr_copy = list(tag_attr)
                        tag_attr_copy[1] = [tag_attr[1]]
                        plain_attr_list_one.append(tag_attr_copy)
                    elif tag_attr[0] == "class":
                        for i in tag_attr[1]:
                            tag_attr_copy = list(tag_attr)
                            tag_attr_copy[1] = [i]
                            plain_attr_list_one.append(tag_attr_copy)
                    elif not tag_attr[1]:
                        continue

            plain_attr_lists.append(self.getListNoneDuple(plain_attr_list_one))

        return plain_attr_lists

    def test_simple_func(self):
        file_path = os.path.join(STATIC_DIR, 'html/mallospace.txt')

        with open(file_path, 'r') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')

        # response = requests.get("http://mallowspace.com/product/list.html?cate_no=24")
        # soup = BeautifulSoup(response.content, 'html.parser')

        title_1 = "Green PVC 디자인 코팅 스키니 테이블매트 노블시리즈"
        title_2 = "Green PVC 사각 테이블매트 퓨어실버화이트 S9"
        title_3 = "Green PVC 디자인 코팅 사각S 테이블매트 노블시리즈"
        title_4 = "Green PVC 사각/스키니 테이블매트"
        price_1 = "14,400원"
        price_2 = "11,800원"

        title_list = [title_1, title_2, title_3]
        all_list = [title_1, title_2, title_3, price_1, price_2]

        # *** 전체 구하기 ***
        lists = self.getPlainParent(soup, all_list)
        pprint(lists)
        print("=" * 150)
        lists = self.getDupCount(lists)
        pprint(lists)
        print("=" * 150)

        max_num = 0
        max_attr = None
        for i in lists:
            if i[1] > max_num:
                max_num = i[1]
                max_attr = i

        # ****************

        # *** 타이틀 구하기 ***

        lists = self.getPlainParent(soup, title_list)
        pprint(lists)
        print("=" * 150)
        lists = self.getDupCount(lists)
        pprint(lists)
        print("=" * 150)

        title_max_num = 0
        title_max_attr = None
        for i in lists:
            if i[1] > title_max_num:
                title_max_num = i[1]
                title_max_attr = i

        # ****************

        print("최종결과본")
        # print("전체 Products의 공통 속성값 => {} : {}".format(max_attr[0][0], max_attr[0][1][0]))
        print("Products의 title 공통 속성값 => {} : {}".format(title_max_attr[0][0], title_max_attr[0][1][0]))

    def test_simple_func2(self):
        file_path = os.path.join(STATIC_DIR, 'html/mallospace.txt')

        with open(file_path, 'r') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')

        title_parser = soup.select("[id*=anchorBoxId_] .name")
        print(len(title_parser))
