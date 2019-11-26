# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import nva.praeventionswissen


class NvaPraeventionswissenLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=nva.praeventionswissen)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'nva.praeventionswissen:default')


NVA_PRAEVENTIONSWISSEN_FIXTURE = NvaPraeventionswissenLayer()


NVA_PRAEVENTIONSWISSEN_INTEGRATION_TESTING = IntegrationTesting(
    bases=(NVA_PRAEVENTIONSWISSEN_FIXTURE,),
    name='NvaPraeventionswissenLayer:IntegrationTesting'
)


NVA_PRAEVENTIONSWISSEN_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(NVA_PRAEVENTIONSWISSEN_FIXTURE,),
    name='NvaPraeventionswissenLayer:FunctionalTesting'
)


NVA_PRAEVENTIONSWISSEN_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        NVA_PRAEVENTIONSWISSEN_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='NvaPraeventionswissenLayer:AcceptanceTesting'
)
