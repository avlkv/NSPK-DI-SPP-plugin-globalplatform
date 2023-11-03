"""
Парсер плагина SPP

1/2 документ плагина
"""
import logging
import os
import time
from datetime import datetime
from src.spp.types import SPP_document
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import requests
from lxml import etree


class GLOBAL_PLATFORM:
    """
    Класс парсера плагина SPP

    :warning Все необходимое для работы парсера должно находится внутри этого класса

    :_content_document: Это список объектов документа. При старте класса этот список должен обнулиться,
                        а затем по мере обработки источника - заполняться.


    """
    DOWNLOAD_DIR_PATH = r'C:\Users\Artyom\Downloads\globalplatform\downloads'
    SOURCE_NAME = 'global_platform'
    HOST = 'https://globalplatform.org/'
    url_template = f'{HOST}specs-library/'
    date_begin = datetime(2019, 1, 1)

    _content_document: list[SPP_document]

    def __init__(self, webdriver, *args, **kwargs):
        """
        Конструктор класса парсера

        По умолчанию внего ничего не передается, но если требуется (например: driver селениума), то нужно будет
        заполнить конфигурацию
        """
        # Обнуление списка
        self._content_document = []

        self.driver = webdriver

        # Логер должен подключаться так. Вся настройка лежит на платформе
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Parser class init completed")
        self.logger.info(f"Set source: {self.SOURCE_NAME}")
        ...

    def content(self) -> list[SPP_document]:
        """
        Главный метод парсера. Его будет вызывать платформа. Он вызывает метод _parse и возвращает список документов
        :return:
        :rtype:
        """
        self.logger.debug("Parse process start")
        self._parse()
        self.logger.debug("Parse process finished")
        return self._content_document

    def _parse(self):
        """
        Метод, занимающийся парсингом. Он добавляет в _content_document документы, которые получилось обработать
        :return:
        :rtype:
        """
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {self.HOST}")

        # ========================================
        # Тут должен находится блок кода, отвечающий за парсинг конкретного источника
        # -
        self.logger.info(f'Загрузка страницы: {self.url_template}')
        self.driver.get(url=f"{self.url_template}")
        time.sleep(5)
        self.driver.find_element(By.XPATH, '//*[@id="cookie_action_close_header"]').click()
        url = self.driver.current_url
        script = "return fetch('{}').then(response => response.status)".format(url)
        response = self.driver.execute_script(script)
        try:
            print(response)
            if response == 200:
                self._parse_page()
            else:
                self.logger.error('Не удалось загрузить страницы')
        except Exception as _ex:
            print(_ex)
        # Логирование найденного документа
        # self.logger.info(self._find_document_text_for_logger(document))

        # ---
        # ========================================
        ...

    def delete_files_in_folder(self, folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f'Ошибка при удалении файла {file_path}. {e}')

    def repalcer(self, stroka: str):
        stroka.replace(r"\t", "").replace(r'\n', "")
        while "  " in stroka:
            stroka = stroka.replace('  ', " ")
        while stroka[0] == ' ':
            stroka = stroka[1:]
        while stroka[-1] == " ":
            stroka = stroka[:-1]
        return stroka

    def _parse_page(self):
        opener = '{'
        closer = '}'
        page = self.driver.page_source
        soup = BeautifulSoup((BeautifulSoup(page, 'html.parser')).find('div', class_='panel-group').prettify(), 'html.parser')
        divs = soup.find_all('div', class_='panel panel-default')
        for div in divs:
            title = div.find('h4', class_='panel-title').find('a').get_text()
            doc_versions_div = div.find('div', class_='panel-collapse collapse').find('div', class_='panel-body general-content')
            div_now_version = doc_versions_div.find('div', class_='row latest-version')
            abstract = etree.HTML(str(div_now_version)).xpath('//div[1]/p')[0].text
            specification_link = etree.HTML(str(div_now_version)).xpath("""//div[2]/a[3]""")[0].get('href')
            print(specification_link)
            self.driver.get(specification_link)
            new_page = self.driver.page_source
            new_soup = BeautifulSoup(new_page, 'html.parser')
            trying_to_download = etree.HTML(str(new_soup)).xpath("""//*[@id="collapse-"]/div/div/div[2]/a[2]""")[0].get('href')
            if "javascript:download_spec" in trying_to_download:
                myp = self.driver.execute_script(f"""
                    function download_spec(media_id) {opener}
                        var popup_width = 500;
                        var res = jQuery.post('https://globalplatform.org/wp-content/themes/globalplatform/ajax/download-spec.php', {opener}file_download: media_id{closer} , function(data) {opener}
                        if(data) {opener}
                            let perem = 'https://globalplatform.org/wp-content/themes/globalplatform/ajax/file-download.php?f='+data;
                            console.log(perem);
                            return perem;
                        {closer} else {opener}
                            console.log('else');
                            lwd_pop_open('https://globalplatform.org/wp-content/themes/globalplatform/ajax/download-spec.php', {opener}popup_width: popup_width, media_id: media_id{closer}, popup_width);
                            {closer}
                        {closer});
                        return res;
                    {closer}
                    return {trying_to_download.replace('javascript:', "")};
                        """)
                if myp == "":
                    time.sleep(5)
                    self.driver.find_element(By.XPATH, """//*[@id="first_name"]""").send_keys("a")
                    self.driver.find_element(By.XPATH, """//*[@id="last_name"]""").send_keys("a")
                    self.driver.find_element(By.XPATH, """//*[@id="company"]""").send_keys("a")
                    self.driver.find_element(By.XPATH, """//*[@id="email"]""").send_keys("a@a.com")
                    self.driver.find_element(By.XPATH, "/html/body/div[9]/div/form/div/div[2]/input").click()
                    time.sleep(4)
                    self.driver.find_element(By.XPATH, "/html/body/div[9]/div/form/div/input").click()
                    time.sleep(8)
                    myp = self.driver.execute_script(f"""
                                        function download_spec(media_id) {opener}
                                            var popup_width = 500;
                                            var res = jQuery.post('https://globalplatform.org/wp-content/themes/globalplatform/ajax/download-spec.php', {opener}file_download: media_id{closer} , function(data) {opener}
                                            if(data) {opener}
                                                let perem = 'https://globalplatform.org/wp-content/themes/globalplatform/ajax/file-download.php?f='+data;
                                                console.log(perem);
                                                return perem;
                                            {closer} else {opener}
                                                console.log('else');
                                                lwd_pop_open('https://globalplatform.org/wp-content/themes/globalplatform/ajax/download-spec.php', {opener}popup_width: popup_width, media_id: media_id{closer}, popup_width);
                                                {closer}
                                            {closer});
                                            return res;
                                        {closer}
                                        return {trying_to_download.replace('javascript:', "")};
                                            """)
                time.sleep(8)
                self.delete_files_in_folder(self.DOWNLOAD_DIR_PATH)
                s = etree.HTML(str(new_soup)).xpath("""//*[@id="heading-"]/h4/a/span""")[0].text.replace("Published ", "").replace('\n', "").replace('\t', '')
                s = self.repalcer(s)
                print(s)
                abstract = self.repalcer(abstract)
                pub_date = datetime.strptime(s, "%b %Y")
                document = SPP_document(
                    None,
                    title=title,
                    abstract=abstract if abstract else None,
                    text=None,
                    web_link=myp,
                    local_link=None,
                    other_data=None,
                    pub_date=pub_date,
                    load_date=None,
                )
                self._content_document.append(document)
                print(document)
                self.logger.debug(self._find_document_text_for_logger(document))

    @staticmethod
    def _find_document_text_for_logger(doc: SPP_document):
        """
        Единый для всех парсеров метод, который подготовит на основе SPP_document строку для логера
        :param doc: Документ, полученный парсером во время своей работы
        :type doc:
        :return: Строка для логера на основе документа
        :rtype:
        """
        return f"Find document | name: {doc.title} | link to web: {doc.web_link} | publication date: {doc.pub_date}"

    @staticmethod
    def some_necessary_method():
        """
        Если для парсинга нужен какой-то метод, то его нужно писать в классе.

        Например: конвертация дат и времени, конвертация версий документов и т. д.
        :return:
        :rtype:
        """
        ...

    @staticmethod
    def nasty_download(driver, path: str, url: str) -> str:
        """
        Метод для "противных" источников. Для разных источника он может отличаться.
        Но основной его задачей является:
            доведение driver селениума до файла непосредственно.

            Например: пройти куки, ввод форм и т. п.

        Метод скачивает документ по пути, указанному в driver, и возвращает имя файла, который был сохранен
        :param driver: WebInstallDriver, должен быть с настроенным местом скачивания
        :_type driver: WebInstallDriver
        :param url:
        :_type url:
        :return:
        :rtype:
        """

        with driver:
            driver.set_page_load_timeout(40)
            driver.get(url=url)
            time.sleep(1)

            # ========================================
            # Тут должен находится блок кода, отвечающий за конкретный источник
            # -
            # ---
            # ========================================

            # Ожидание полной загрузки файла
            while not os.path.exists(path + '/' + url.split('/')[-1]):
                time.sleep(1)

            if os.path.isfile(path + '/' + url.split('/')[-1]):
                # filename
                return url.split('/')[-1]
            else:
                return ""
