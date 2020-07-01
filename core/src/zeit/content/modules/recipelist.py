from lxml.objectify import E
import collections
import zeit.content.modules.interfaces
import zeit.wochenmarkt.interfaces
import zope.interface


class Ingredient(object):

    def __init__(self, code, label, amount, unit, details):
        self.code = code
        self.label = label
        self.amount = amount
        self.unit = unit
        self.details = details

    @classmethod
    def from_xml(cls, node):
        code = node.get('code')
        try:
            name = zope.component.getUtility(
                zeit.wochenmarkt.interfaces.IIngredientsWhitelist).get(
                    code).name
        except AttributeError:
            # Take care of insufficient whitelist data e.g. missing entries.
            return None
        return cls(
            code,
            name,
            node.get('amount'),
            node.get('unit'),
            node.get('details'))


@zope.interface.implementer(zeit.content.modules.interfaces.IRecipeList)
class RecipeList(zeit.edit.block.Element):

    merge_with_previous = (
        zeit.cms.content.property.ObjectPathProperty(
            '.merge_with_previous',
            zeit.content.modules.interfaces.IRecipeList[
                'merge_with_previous']))

    title = zeit.cms.content.property.ObjectPathProperty(
        '.title', zeit.content.modules.interfaces.IRecipeList['title'])

    subheading = zeit.cms.content.property.ObjectPathProperty(
        '.subheading', zeit.content.modules.interfaces.IRecipeList[
            'subheading'])

    searchable_subheading = (
        zeit.cms.content.property.ObjectPathAttributeProperty(
            '.subheading', 'searchable',
            zeit.content.modules.interfaces.IRecipeList[
                'searchable_subheading']))

    complexity = zeit.cms.content.property.ObjectPathProperty(
        '.complexity',
        zeit.content.modules.interfaces.IRecipeList['complexity'])

    time = zeit.cms.content.property.ObjectPathProperty(
        '.time',
        zeit.content.modules.interfaces.IRecipeList['time'])

    servings = zeit.cms.content.property.ObjectPathProperty(
        '.servings',
        zeit.content.modules.interfaces.IRecipeList['servings'])

    @property
    def ingredients(self):
        ingredients = [Ingredient.from_xml(x) for x in self.xml.xpath(
            './ingredient')]
        return [i for i in ingredients if i is not None]

    @ingredients.setter
    def ingredients(self, value):
        for node in self.xml.xpath('./ingredient'):
            node.getparent().remove(node)
        value = self._remove_duplicates(value)
        for item in value:
            self.xml.append(
                E.ingredient(
                    code=item.code,
                    amount=item.amount if hasattr(item, 'amount') else '',
                    unit=item.unit if hasattr(item, 'unit') else '',
                    details=item.details if hasattr(item, 'details') else ''))

    def _remove_duplicates(self, ingredients):
        result = collections.OrderedDict()
        for ingredient in ingredients:
            if ingredient.code not in result:
                result[ingredient.code] = ingredient
        return result.values()
