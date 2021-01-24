import scrapy
from scrapy.exceptions import CloseSpider
from helpers import (yesno_prompt,
                     colors,
                     yesno_isvalid,
                     is_valid_list,
                     loopbreak,
                     eyerelief)


class TurkishSpider(scrapy.Spider):
    name = "turkishspider"
    faillist = []

    def start_requests(self):
        with open('toscrape.txt') as f:
            words = f.readlines()
        urls = ['https://glosbe.com/tr/en/' +
                word[:-1] for word in words]
        # urls = ['https://glosbe.com/tr/en/kanepe']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        satisfied = False
        exitvalve = 0
        unwanted_text = ['<div dir="ltr" class="span6">',
                         '<b>',
                         '</b>',
                         '</div>',
                         '<div dir="ltr">']
        while not satisfied:
            exitvalve += 1
            if exitvalve > 1000:
                raise CloseSpider(loopbreak)
            n = 0
            exlist = response.xpath('//div[@class="examples"]/div[@class="row-fluid"]/div[@dir="ltr"]').getall()
            trlist = response.xpath('//div[@class="examples"]/div[@class="row-fluid"]/div[@lang="en"]/div[@dir="ltr"]').getall()

            eyerelief()
            if len(exlist) == 0:
                print(f'{colors.warning("ERROR - NO RESULTS RETURNED; SKIPPING" + response.url[25:])}')
                self.faillist.append(response.url[25:])
                break
            exlist_clean = []
            trlist_clean = []
            for ex, tr in zip(exlist, trlist):
                ex_clean = ex
                tr_clean = tr
                for unwanted in unwanted_text:
                    ex_clean = ex_clean.replace(unwanted, '')
                    tr_clean = tr_clean.replace(unwanted, '')
                exlist_clean.append(ex_clean)
                trlist_clean.append(tr_clean)
                print(f'{n}\n{colors.bluetext(ex_clean)}\n{colors.information(tr_clean)}')
                n += 1
            eyerelief()
            userchoice = input(
                colors.prompt(
                    'Enter the numbers of the examples above you would like'
                    'to save, separated by commas:\n'
                )
            )
            exitvalve2 = 0
            while not is_valid_list(userchoice,
                                    exlist) or not is_valid_list(userchoice,
                                                                 trlist):
                exitvalve2 += 1
                if exitvalve2 > 1000:
                    raise CloseSpider(loopbreak)
                    break
                userchoice = input(
                    colors.warning(
                        'Invalid choice. Please enter the numbers of the '
                        'examples you would like to save separated by '
                        'commas:\n'
                    )
                )
            userchoice = userchoice.split(',')
            userchoice = [int(s) for s in userchoice]
            userchoice = set(userchoice)
            print(colors.prompt("you selected:"))
            for num in userchoice:
                print(colors.parrot(f'{num}\n') +
                      colors.bluetext(f'{exlist_clean[num]}\n') +
                      colors.information(f'{trlist_clean[num]}\n'))
            if yesno_prompt(
                colors.prompt('Is that correct? y/n:\n'),
                colors.warning('Invalid entry. Please enter y or n:\n')
            ):
                satisfied = True
            with open('examples.txt', 'a') as output:
                for num in userchoice:
                    output.write(f'{exlist_clean[num]}|{trlist_clean[num]}\n')
