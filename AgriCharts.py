from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import commodity

__author__ = 'Vikram Bankar'


class AgriCharts:
    """
        Methods:
        serialize
        extract_html

    """
    #URL of Agmarknet State wise Data Reporting
    url = "http://agmarknet.nic.in/agnew/NationalBEnglish/MarketDailyStateWise.aspx"

    #Filestore for storing temporary files that hold the data till it is written into the database.
    filestore = "C:\Users\Vikram\Documents\Visual Studio 2010\Projects\Agmarknet\Agmarknet\FileStore"

    #Set production = False when testing, base your tests on this boolean
    production = False

    #Starting date, data from this point onwards will be fetched.
    import datetime
    current_fetching_date = datetime.datetime(2000, 01, 01)

    #Today
    from datetime import datetime
    today = datetime.today()

    def get_current_fetching_date(self, increment=1):
        from os import listdir
        filelist = listdir(self.filestore)
        if filelist is not None:
            new_list = []
            for name in filelist:
                date_string = name.replace('.bin', '').split('-')
                date_string.reverse()
                ints = []
                import datetime
                for number in date_string:
                    ints.append(int(number))
                new_list.append(datetime.date(*ints))
            new_list.sort(reverse=False)
            return new_list.pop() + datetime.timedelta(days=increment)
        else:
            return datetime.date(2000, 01, 01)

    def __init__(self):
        """
        Default Constructor for AgriChart.
        Sets: last_recorded_date & current_fetching_date.
        Initiates collect_data.
        """
        self.current_fetching_date = self.get_current_fetching_date()

        #Using a Firefox driver
        self.driver = webdriver.Firefox()
        self.driver.set_page_load_timeout(65)

    @staticmethod
    def serialize(object_to_be_serialized, result_file):
            #Open if exists else create and open:
            import os.path
            if not os.path.isfile(result_file):
                #This is the only way to create a file in python (sadly)
                open(result_file, 'a').close()
            result = open(result_file, "w")
            import umsgpack
            result.write(umsgpack.dumps(object_to_be_serialized))
            result.close()

    def extract_html(self):
        items = []
        #try:
        if not self.production:
            self.driver.get("file:///C:/Users/Vikram/Desktop/State-wise%20Data%20Reporting.htm")

        xpath = "//table[@id='gridRecords']/tbody/tr[position()>1]"
        items = self.parse_report_table(self.driver.find_elements_by_xpath(xpath))
        filename = "Testing.msg"
        
        if self.production:
            filename = self.filestore + "/" + self.current_fetching_date.strftime("%d-%m-%Y")+".msg"
        
        self.serialize(items, filename)
        """except:
            pass
        finally:
            pass"""

    @staticmethod
    def get_list_of_items(html_node):
        """
        Get whitespace delimited data from each field in a row, blank rows omitted.
        :param html_node: The row as a selenium web element
        :return: string of whitespace delimited data from each field in a row.
        """
        items = html_node.find_elements_by_tag_name('td')
        results = []

        #include the only results with something inside them!
        for td in items:
            txt = str(td.text).strip()
            if not txt == '':
                results.append(txt)

        return results

    def parse_report_table(self, html_nodes):

        """
        Performs parsing of the report page.
        :param html_nodes: Rows from gridRecords table.
        :return: resulting list of commodity objects.
        """
        items = []
        for i in xrange(0, len(html_nodes)):
            inner_text = str(html_nodes[i].text).strip()
            if inner_text == "":
                continue
            type_of_commodity = ""
            if inner_text.startswith("Market:"):
                market = inner_text.split(':').pop(-1).strip()
                result = []
                result_varieties = []
                #While the table has rows and there is no new market.
                while i + 1 < len(html_nodes) and not html_nodes[i+1].text.strip().startswith("Market:"):
                    i += 1
                    inner_text = str(html_nodes[i].text).strip()
                    if inner_text == "":
                        continue
                    if not inner_text.__contains__(' '):
                        type_of_commodity = inner_text
                        i += 1

                    #parse commodity
                    values = self.get_list_of_items(html_nodes[i])

                    #if there are full set of values (which is = 8)
                    if len(values) == 8:
                        if values[1] == "NR":
                            temp = 0
                        else:
                            temp = values[1]


                        """
                        Older Way
                        """
                        result.append(copy.deepcopy(commodity.Commodity().new(market, type_of_commodity, values[0],
                                        temp, values[2], values[3], values[4], values[5], values[6], values[7],
                                            self.current_fetching_date)))

                        """
                        Experimental
                        result.append(
                          copy.deepcopy(
                            commodity.Commodity().new(
                              market, type_of_commodity, values[0], values[2:8], self.current_fetching_date)))
                        """

                        result_varieties = []

                        """
                        If items in row = 5, same commodity but different variety
                        for example Onion has many varieties: Red / White etc.
                        """

                        while i+1 < len(html_nodes):
                            values = self.get_list_of_items(html_nodes[i+1])
                            if len(values) != 5:
                                break
                            result_varieties.append(commodity.Variety().new(values[0], values[1], values[2], values[3],
                                                                            values[4]))
                            i += 1
                        import copy
                        for variety in result_varieties:
                            temp_result_copy = copy.copy(result[-1])
                            temp_result_copy.variety = copy.deepcopy(variety)
                            result.append(temp_result_copy)

                #Add the results to the Items list.
                items.extend(result)
                result = []
                #While Block Ends Here.
        #For Loop Ends
        return items

    def check_and_stall(self):
        delay = 5
        while self.driver.title.__contains__('Error'):
            from time import sleep
            time.sleep(delay)
            self.driver.get(self.url)
            if delay < 20:
                delay += 5

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def set_defaults(self, recursive=False):
        try:
            # Select State = Maharashtra
            self.driver.find_element_by_xpath("//select[@id='cboState']/option[text()='Maharashtra']").click()

            #Select Month = Currently Fetching Month
            month = self.current_fetching_date.strftime("%B")
            self.driver.find_element_by_xpath("//select[@id='cboMonth']/option[text()='"+month+"']").click()

            #Select Year = Currently Fetching Year
            year = self.current_fetching_date.strftime("%Y")
            self.driver.find_element_by_xpath("//select[@id='cboYear']/option[text()='"+year+"']").click()
        except TimeoutException, e:
            self.check_and_stall()
            if not recursive:
                self.set_defaults(True)
            else:
                raise BaseException()

    def get_links(self):
        a_elements = self.driver.find_elements_by_xpath("//table[@id='Calendar1']/tbody/tr/td/a")
        links = []
        for item in a_elements:
            attrib = str(item.get_attribute('href'))
            if attrib is not None and attrib != "" and attrib.startswith("javascript:__doPostBack('Calendar1','"):
                    links.append(item)
        return links

    def collect_data(self):
        self.driver.get(self.url)
        self.check_and_stall()

        #While Database is not updated to the current date.
        while self.current_fetching_date < self.today:

            #Load all the urls in links
            links = []
            link_count = 1
            i = 0
            #Loop for each link in the list.
            while i < link_count:
                #Prepare!
                self.check_and_stall()
                self.set_defaults()

                #Get links
                links = self.get_links()

                #Link count is set here.
                link_count = len(links)
                try:
                    #in case: if the site is down, links = 0, till then we need to stall.
                    if links == 0:
                        self.check_and_stall()
                        self.set_defaults()

                    #Skip those links whose records have already been fetched.
                    while int(links[i].text) < self.current_fetching_date.day:
                        i += 1

                    #looping till links are remaining.
                    if i < link_count:
                        links[i].click()
                        self.driver.find_element_by_id("btnSubmit").click()
                        if self.is_element_present(how=By.ID, what="gridRecords"):
                                #2nd Measure of protection: Check if the records exists:
                                # extract only if they are not already extracted

                            title = str(self.driver.find_element_by_css_selector("span#lblTitle").text).split(" ")\
                                        .pop().replace('/', '-') + ".bin"
                            from os import listdir

                            if os.listdir(self.filestore).count(title) == 0:
                                self.extract_html()

                            self.driver.back()
                            self.set_defaults()
                            links = self.get_links()
                        elif str(self.driver.title).lower() == "error":
                            self.check_and_stall()
                            i -= 1
                            continue
                except TimeoutException, e:
                    self.check_and_stall()
                except Exception, ex:
                    return False
                finally:
                    pass
                i += 1
        return True
