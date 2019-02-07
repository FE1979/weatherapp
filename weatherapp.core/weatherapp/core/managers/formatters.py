from html import escape, unescape

from abstract.abstract import Formatter

class TableFormatter(Formatter):

    def print_out(self, weather_info, title):
        """
        Returns weather info for output as nice table
        """

        output_data = self._make_printable(weather_info)

        return self.nice_output(output_data, title)

    @staticmethod
    def nice_output(table_data, title):
        """ This forms nice table output for printing or saving to the file
        """

        nice_txt = ''
        first_column_len = len(max(table_data[0], key = lambda item: len(item))) + 2
        second_column_len = len(max(table_data[1], key = lambda item: len(item))) + 2
        header_len = len(title)

        if header_len > first_column_len + second_column_len:
            second_column_len = header_len - first_column_len

        width = first_column_len + second_column_len + 1
        counter = len(table_data[0])
        i = 0

        #print top of table with title
        nice_txt = '+' + '-'*(width) + '+' + '\n'
        nice_txt = nice_txt + '|' + title.center(width, ' ') + '|' + '\n'
        nice_txt = nice_txt +'+' + '-'*(first_column_len) \
                            + '+' + '-'*(second_column_len) + '+' + '\n'

        while i < counter: #print out headers and values
            nice_txt = nice_txt \
                + '| ' + str(table_data[0][i]).ljust(first_column_len-1, ' ')
            nice_txt = nice_txt \
                + '| ' + str(table_data[1][i]).ljust(second_column_len-1, ' ') + '|'
            nice_txt = nice_txt + '\n'
            i += 1
            pass
        #bottom line
        nice_txt = nice_txt \
                + '+' + '-'*(first_column_len) + '+' + '-'*(second_column_len) + '+'
        #separation blank line
        nice_txt = nice_txt + '\n'

        return nice_txt

    @staticmethod
    def _make_printable(weather_info):
        """ Transform weather data to printable format
            headers_dict - translation dictionary
            temperature_heads - to insert Celsius sign if needed
            print_order - to define which way weather_info will show
        """
        headers_dict = {'Temperature': 'Температура',
                        'RealFeel': 'Відчувається як',
                        'Condition': 'На небі',
                        'Max': 'Максимальна', 'Min': 'Мінімальна', 'Av': 'Середня',
                        'Num': 'Прогноз на, годин',
                        'Deg': f"{unescape('&deg')}C",
                        'Next_day_temp': 'Максимальна вдень',
                        'Next_day_temp_max': 'Максимальна вдень', #for RP5
                        'Next_day_temp_min': 'Мінімальна вдень', #for RP5
                        'Next_day_RF': 'Відчуватиметься вдень як',
                        'Next_day_condition': 'На небі вдень буде',
                        'Next_night_temp': 'Мінімальна вночі',
                        'Next_night_RF': 'Відчуватиметься вночі як',
                        'Next_night_condition': 'На небі вночі буде'}
        temperature_heads = ['Temperature', 'RealFeel', 'Max', 'Min', 'Av',
                            'Next_day_temp', 'Next_day_RF', 'Next_night_temp',
                            'Next_night_RF', 'Next_day_temp_max', 'Next_day_temp_min']
        print_order = ['Temperature', 'RealFeel', 'Condition', 'Num', 'Max', 'Min', 'Av',
                        'Next_day_temp', 'Next_day_temp_max', 'Next_day_temp_min',
                        'Next_day_RF', 'Next_day_condition',
                        'Next_night_temp', 'Next_night_RF', 'Next_night_condition']
        output_data = [[],[]]

        for item in print_order: #in printing order
            if item in weather_info.keys(): #if there is a data
                if item in temperature_heads: #if we need to show Celsius
                    output_data[0].append(headers_dict[item])
                    if weather_info[item] != '': #if temp is not blank
                        output_data[1].append(f"{weather_info[item]:.0f}" + ' ' + headers_dict['Deg'])
                    else:
                        output_data[1].append(f"{weather_info[item]}" + ' ' + headers_dict['Deg'])
                else:
                    output_data[0].append(headers_dict[item])
                    output_data[1].append(str(weather_info[item]))
            else:
                pass

        return output_data


class PlainText(Formatter):

    headers_dict = {'Temperature': 'Температура',
                    'RealFeel': 'Відчувається як',
                    'Condition': 'На небі',
                    'Max': 'Максимальна', 'Min': 'Мінімальна', 'Av': 'Середня',
                    'Num': 'Прогноз на, годин',
                    'Deg': f"{unescape('&deg')}C",
                    'Next_day_temp': 'Максимальна вдень',
                    'Next_day_temp_max': 'Максимальна вдень', #for RP5
                    'Next_day_temp_min': 'Мінімальна вдень', #for RP5
                    'Next_day_RF': 'Відчуватиметься вдень як',
                    'Next_day_condition': 'На небі вдень буде',
                    'Next_night_temp': 'Мінімальна вночі',
                    'Next_night_RF': 'Відчуватиметься вночі як',
                    'Next_night_condition': 'На небі вночі буде'}


    def print_out(self, weather_info, title):
        """ Prints weather info as plain text """

        output_data = "\n" + title + "\n"

        for item in weather_info:
            output_data = f"{output_data}\n{self.headers_dict[item]}: {weather_info[item]}"

        return output_data + "\n"
