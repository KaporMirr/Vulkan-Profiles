#!/usr/bin/python3
#
# Copyright (c) 2021-2022 LunarG, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Daniel Rakos, RasterGrid

import os
import re
import argparse
import xml.etree.ElementTree as etree
import json

COPYRIGHT_HEADER = '''/**
 * Copyright (c) 2021-2022 LunarG, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License")
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * DO NOT EDIT: This file is generated.
 */
'''

H_HEADER = '''
#ifndef VULKAN_PROFILES_
#define VULKAN_PROFILES_ 1

#define VPAPI_ATTR

#ifdef __cplusplus
    extern "C" {
#endif

#include <vulkan/vulkan_core.h>
#ifdef VK_ENABLE_BETA_EXTENSIONS
#include <vulkan/vulkan_beta.h>

#endif
'''

H_FOOTER = '''
#ifdef __cplusplus
}
#endif

#endif //VULKAN_PROFILES_
'''

CPP_HEADER = '''
#include <vulkan/vulkan_profiles.h>
#include <stddef.h>
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <vector>
#include <algorithm>

#define _vpArraySize(arr) static_cast<uint32_t>(sizeof(arr) / sizeof(arr[0]))
'''

HPP_HEADER = '''
#ifndef VULKAN_PROFILES_
#define VULKAN_PROFILES_ 1

#define VPAPI_ATTR inline

#include <vulkan/vulkan_core.h>
#ifdef VK_ENABLE_BETA_EXTENSIONS
#include <vulkan/vulkan_beta.h>
#endif
#include <stddef.h>
#include <string.h>
#include <assert.h>
#include <stdint.h>
#include <vector>
#include <algorithm>

#define _vpArraySize(arr) static_cast<uint32_t>(sizeof(arr) / sizeof(arr[0]))
'''

HPP_FOOTER = '''
#endif //VULKAN_PROFILES_
'''

API_DEFS = '''
#define VP_MAX_PROFILE_NAME_SIZE 256U

typedef struct VpProfileProperties {
    char        profileName[VP_MAX_PROFILE_NAME_SIZE];
    uint32_t    specVersion;
} VpProfileProperties;

typedef enum VpInstanceCreateFlagBits {
    VP_INSTANCE_CREATE_MERGE_EXTENSIONS_BIT = 0x00000001,
    VP_INSTANCE_CREATE_OVERRIDE_EXTENSIONS_BIT = 0x00000002,
    VP_INSTANCE_CREATE_OVERRIDE_API_VERSION_BIT = 0x00000004,

    VP_INSTANCE_CREATE_FLAG_BITS_MAX_ENUM = 0x7FFFFFFF
} VpInstanceCreateFlagBits;
typedef VkFlags VpInstanceCreateFlags;

typedef struct VpInstanceCreateInfo {
    const VkInstanceCreateInfo* pCreateInfo;
    const VpProfileProperties*  pProfile;
    VpInstanceCreateFlags       flags;
} VpInstanceCreateInfo;

typedef enum VpDeviceCreateFlagBits {
    VP_DEVICE_CREATE_DISABLE_ROBUST_BUFFER_ACCESS_BIT = 0x00000001,
    VP_DEVICE_CREATE_DISABLE_ROBUST_IMAGE_ACCESS_BIT = 0x00000002,
    VP_DEVICE_CREATE_MERGE_EXTENSIONS_BIT = 0x00000004,
    VP_DEVICE_CREATE_OVERRIDE_EXTENSIONS_BIT = 0x00000008,

    VP_DEVICE_CREATE_DISABLE_ROBUST_ACCESS_BIT =
        VP_DEVICE_CREATE_DISABLE_ROBUST_BUFFER_ACCESS_BIT | VP_DEVICE_CREATE_DISABLE_ROBUST_IMAGE_ACCESS_BIT,
    VP_DEVICE_CREATE_FLAG_BITS_MAX_ENUM = 0x7FFFFFFF
} VpDeviceCreateFlagBits;
typedef VkFlags VpDeviceCreateFlags;

typedef struct VpDeviceCreateInfo {
    const VkDeviceCreateInfo*   pCreateInfo;
    const VpProfileProperties*  pProfile;
    VpDeviceCreateFlags         flags;
} VpDeviceCreateInfo;

// Query the list of available profiles in the library
VPAPI_ATTR VkResult vpGetProfiles(uint32_t *pPropertyCount, VpProfileProperties *pProperties);

// List the recommended fallback profiles of a profile
VPAPI_ATTR VkResult vpGetProfileFallbacks(const VpProfileProperties *pProfile, uint32_t *pPropertyCount, VpProfileProperties *pProperties);

// Check whether a profile is supported at the instance level
VPAPI_ATTR VkResult vpGetInstanceProfileSupport(const char *pLayerName, const VpProfileProperties *pProfile, VkBool32 *pSupported);

// Create a VkInstance with the profile instance extensions enabled
VPAPI_ATTR VkResult vpCreateInstance(const VpInstanceCreateInfo *pCreateInfo,
                                     const VkAllocationCallbacks *pAllocator, VkInstance *pInstance);

// Check whether a profile is supported by the physical device
VPAPI_ATTR VkResult vpGetDeviceProfileSupport(VkPhysicalDevice physicalDevice, const VpProfileProperties *pProfile, VkBool32 *pSupported);

// Create a VkDevice with the profile features and device extensions enabled
VPAPI_ATTR VkResult vpCreateDevice(VkPhysicalDevice physicalDevice, const VpDeviceCreateInfo *pCreateInfo,
                                   const VkAllocationCallbacks *pAllocator, VkDevice *pDevice);

// Query the list of instance extensions of a profile
VPAPI_ATTR VkResult vpGetProfileInstanceExtensionProperties(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                            VkExtensionProperties *pProperties);

// Query the list of device extensions of a profile
VPAPI_ATTR VkResult vpGetProfileDeviceExtensionProperties(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                          VkExtensionProperties *pProperties);

// Fill the pNext Vulkan structures with the requirements of a profile
VPAPI_ATTR void vpGetProfileStructures(const VpProfileProperties *pProfile, void *pNext);

typedef enum VpStructureArea {
    VP_STRUCTURE_FEATURES = 0,  // A Vulkan structure specified to expose features
    VP_STRUCTURE_PROPERTIES     // A Vulkan structure specified to expose properties
} VpStructureArea;

typedef struct VpStructureProperties {
    VkStructureType type;
    VpStructureArea area;
} VpStructureProperties;

// Query the list of structures used to specify requirements of a profile
VPAPI_ATTR VkResult vpGetProfileStructureProperties(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                    VpStructureProperties *pProperties);

// Query the list of formats with specified requirements by a profile
VPAPI_ATTR VkResult vpGetProfileFormats(const VpProfileProperties *pProfile, uint32_t *pFormatCount, VkFormat *pFormats);

// Query the requirements of a format for a profile
VPAPI_ATTR void vpGetProfileFormatProperties(const VpProfileProperties *pProfile, VkFormat format, void *pNext);

// Query the requirements of queue families by a profile
VPAPI_ATTR VkResult vpGetProfileQueueFamilies(const VpProfileProperties *pProfile, uint32_t *pPropertyCount, VkQueueFamilyProperties *pProperties);
'''

PRIVATE_IMPL_BODY = '''
struct _vpProfileDesc {
    const char*                     name;
    uint32_t                        specVersion;
    uint32_t                        minApiVersion;
    const VkExtensionProperties*    pInstanceExtensions;
    uint32_t                        instanceExtensionCount;
    const VkExtensionProperties*    pDeviceExtensions;
    uint32_t                        deviceExtensionCount;
};

VPAPI_ATTR const _vpProfileDesc* _vpGetProfileDesc(const _vpProfileDesc* pProfiles, const char name[VP_MAX_PROFILE_NAME_SIZE]) {
    while (pProfiles->name != nullptr) {
        if (strncmp(pProfiles->name, name, VP_MAX_PROFILE_NAME_SIZE) == 0) return pProfiles;
        pProfiles++;
    }
    return nullptr;
}

VPAPI_ATTR bool _vpCheckExtension(const VkExtensionProperties *supportedProperties, size_t supportedSize,
                                  const char *requestedExtension, uint32_t expectedVersion = 0) {
    for (size_t i = 0, n = supportedSize; i < n; ++i) {
        if (strcmp(supportedProperties[i].extensionName, requestedExtension) == 0) {
            return supportedProperties[i].specVersion > expectedVersion;
        }
    }
    return false;
}

VPAPI_ATTR bool _vpCheckMemoryProperty(const VkPhysicalDeviceMemoryProperties &memoryProperties,
                                       const VkMemoryPropertyFlags &memoryPropertyFlags) {
    assert(&memoryProperties != nullptr);

    for (uint32_t i = 0, n = memoryProperties.memoryTypeCount; i < n; ++i) {
        if ((memoryProperties.memoryTypes[i].propertyFlags & memoryPropertyFlags) == memoryPropertyFlags) return true;
    }

    return false;
}

VPAPI_ATTR bool _vpCheckFormatProperty(const VkFormatProperties2 *deviceProps, const VpFormatProperties &profileProps) {
    if ((deviceProps->formatProperties.linearTilingFeatures & profileProps.linearTilingFeatures) !=
        profileProps.linearTilingFeatures) {
        return false;
    } else if ((deviceProps->formatProperties.optimalTilingFeatures & profileProps.optimalTilingFeatures) !=
               profileProps.optimalTilingFeatures) {
        return false;
    } else if ((deviceProps->formatProperties.bufferFeatures & profileProps.bufferFeatures) != profileProps.bufferFeatures) {
        return false;
    }

    return true;
}

VPAPI_ATTR bool _vpCheckQueueFamilyProperty(const VkQueueFamilyProperties *queueFamilyProperties,
                                            uint32_t queueFamilyPropertiesCount,
                                            const VkQueueFamilyProperties &profileQueueFamilyPropertie) {
    assert(queueFamilyProperties != nullptr);

    for (uint32_t i = 0, n = queueFamilyPropertiesCount; i < n; ++i) {
        if (queueFamilyProperties[i].queueCount < profileQueueFamilyPropertie.queueCount) {
            continue;
        } else if (queueFamilyProperties[i].timestampValidBits < profileQueueFamilyPropertie.timestampValidBits) {
            continue;
        } else if (queueFamilyProperties[i].minImageTransferGranularity.width >
                   profileQueueFamilyPropertie.minImageTransferGranularity.width) {
            continue;
        } else if (queueFamilyProperties[i].minImageTransferGranularity.height >
                   profileQueueFamilyPropertie.minImageTransferGranularity.height) {
            continue;
        } else if (queueFamilyProperties[i].minImageTransferGranularity.depth >
                   profileQueueFamilyPropertie.minImageTransferGranularity.depth) {
            continue;
        } else if ((queueFamilyProperties[i].queueFlags & profileQueueFamilyPropertie.queueFlags) !=
                   profileQueueFamilyPropertie.queueFlags) {
            continue;
        }

        return true;
    }

    return false;
}

VPAPI_ATTR void _vpGetInstanceExtensions(const VpInstanceCreateInfo *pCreateInfo, uint32_t propertyCount,
                                         const VkExtensionProperties *pProperties, std::vector<const char *> &extensions) {
    if (pCreateInfo->flags & VP_INSTANCE_CREATE_MERGE_EXTENSIONS_BIT) {
        for (int i = 0, n = propertyCount; i < n; ++i) {
            extensions.push_back(pProperties[i].extensionName);
        }

        for (uint32_t i = 0; i < pCreateInfo->pCreateInfo->enabledExtensionCount; ++i) {
            if (_vpCheckExtension(pProperties, propertyCount, pCreateInfo->pCreateInfo->ppEnabledExtensionNames[i])) {
                continue;
            }
            extensions.push_back(pCreateInfo->pCreateInfo->ppEnabledExtensionNames[i]);
        }
    } else {  // or VP_INSTANCE_CREATE_OVERRIDE_EXTENSIONS_BIT
        for (int i = 0, n = pCreateInfo->pCreateInfo->enabledExtensionCount; i < n; ++i) {
            extensions.push_back(pCreateInfo->pCreateInfo->ppEnabledExtensionNames[i]);
        }
    }
}

VPAPI_ATTR void _vpGetDeviceExtensions(const VpDeviceCreateInfo *pCreateInfo, uint32_t propertyCount,
                                       const VkExtensionProperties *pProperties, std::vector<const char *> &extensions) {
    if (pCreateInfo->flags & VP_DEVICE_CREATE_MERGE_EXTENSIONS_BIT) {
        for (int i = 0, n = propertyCount; i < n; ++i) {
            extensions.push_back(pProperties[i].extensionName);
        }

        for (uint32_t i = 0; i < pCreateInfo->pCreateInfo->enabledExtensionCount; ++i) {
            if (_vpCheckExtension(pProperties, propertyCount, pCreateInfo->pCreateInfo->ppEnabledExtensionNames[i])) {
                continue;
            }
            extensions.push_back(pCreateInfo->pCreateInfo->ppEnabledExtensionNames[i]);
        }
    } else {  // or VP_DEVICE_CREATE_OVERRIDE_EXTENSIONS_BIT
        for (int i = 0, n = pCreateInfo->pCreateInfo->enabledExtensionCount; i < n; ++i) {
            extensions.push_back(pCreateInfo->pCreateInfo->ppEnabledExtensionNames[i]);
        }
    }
}

VPAPI_ATTR const void* _vpGetStructure(const void* pNext, VkStructureType type) {
    const VkBaseOutStructure *p = static_cast<const VkBaseOutStructure*>(pNext);
    while (p != nullptr) {
        if (p->sType == type) return p;
        p = p->pNext;
    }
    return nullptr;
}
'''

PUBLIC_IMPL_BODY = '''
VPAPI_ATTR VkResult vpGetInstanceProfileSupport(const char *pLayerName, const VpProfileProperties *pProfile, VkBool32 *pSupported) {
    assert(pProfile != nullptr);
    assert(pSupported != nullptr);
    VkResult result = VK_SUCCESS;

    uint32_t apiVersion;
    vkEnumerateInstanceVersion(&apiVersion);

    uint32_t extCount;
    result = vkEnumerateInstanceExtensionProperties(pLayerName, &extCount, nullptr);
    if (result != VK_SUCCESS) return result;
    std::vector<VkExtensionProperties> ext(extCount);
    result = vkEnumerateInstanceExtensionProperties(pLayerName, &extCount, ext.data());
    if (result != VK_SUCCESS) return result;

    *pSupported = VK_FALSE;

    const _vpProfileDesc* pDesc = _vpGetProfileDesc(_vpProfiles, pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    if (pDesc->specVersion < pProfile->specVersion) return result;

    if (VK_VERSION_PATCH(apiVersion) < VK_VERSION_PATCH(pDesc->minApiVersion)) return result;

    for (uint32_t i = 0; i < pDesc->instanceExtensionCount; ++i) {
        if (!_vpCheckExtension(ext.data(), ext.size(),
            pDesc->pInstanceExtensions[i].extensionName,
            pDesc->pInstanceExtensions[i].specVersion)) return result;
    }

    *pSupported = VK_TRUE;
    return result;
}

VPAPI_ATTR VkResult vpCreateInstance(const VpInstanceCreateInfo *pCreateInfo,
                                     const VkAllocationCallbacks *pAllocator, VkInstance *pInstance) {
    VkInstanceCreateInfo createInfo{ VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO };
    VkApplicationInfo appInfo{ VK_STRUCTURE_TYPE_APPLICATION_INFO };
    std::vector<const char*> extensions;
    VkInstanceCreateInfo* pInstanceCreateInfo = nullptr;
    VkExtensionProperties* pProfileExtensions = nullptr;
    uint32_t profileExtensionCount = 0;

    if (pCreateInfo != nullptr && pCreateInfo->pCreateInfo != nullptr) {
        createInfo = *pCreateInfo->pCreateInfo;
        pInstanceCreateInfo = &createInfo;

        const _vpProfileDesc* pDesc = nullptr;
        if (pCreateInfo->pProfile != nullptr) {
            pDesc = _vpGetProfileDesc(_vpProfiles, pCreateInfo->pProfile->profileName);
            if (pDesc == nullptr) return VK_ERROR_UNKNOWN;
        }

        if (pDesc != nullptr && pDesc->pInstanceExtensions != nullptr) {
            _vpGetInstanceExtensions(pCreateInfo, pDesc->instanceExtensionCount, pDesc->pInstanceExtensions, extensions);
            createInfo.enabledExtensionCount = static_cast<uint32_t>(extensions.size());
            createInfo.ppEnabledExtensionNames = extensions.data();
        }

        if (pCreateInfo->flags & VP_INSTANCE_CREATE_OVERRIDE_API_VERSION_BIT) {
            if (createInfo.pApplicationInfo != nullptr) {
                appInfo = *createInfo.pApplicationInfo;
            }
            createInfo.pApplicationInfo = &appInfo;
            appInfo.apiVersion = pDesc->minApiVersion;
        }
    }

    return vkCreateInstance(pInstanceCreateInfo, pAllocator, pInstance);
}

VPAPI_ATTR VkResult vpGetProfileInstanceExtensionProperties(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                            VkExtensionProperties *pProperties) {
    VkResult result = VK_SUCCESS;

    const _vpProfileDesc* pDesc = _vpGetProfileDesc(_vpProfiles, pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    if (pProperties == nullptr) {
        *pPropertyCount = pDesc->instanceExtensionCount;
    } else {
        if (*pPropertyCount < pDesc->instanceExtensionCount) {
            result = VK_INCOMPLETE;
        } else {
            *pPropertyCount = pDesc->instanceExtensionCount;
        }
        for (uint32_t i = 0; i < *pPropertyCount; ++i) {
            pProperties[i] = pDesc->pInstanceExtensions[i];
        }
    }
    return result;
}

VPAPI_ATTR VkResult vpGetProfileDeviceExtensionProperties(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                          VkExtensionProperties *pProperties) {
    VkResult result = VK_SUCCESS;

    const _vpProfileDesc* pDesc = _vpGetProfileDesc(_vpProfiles, pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    if (pProperties == nullptr) {
        *pPropertyCount = pDesc->deviceExtensionCount;
    } else {
        if (*pPropertyCount < pDesc->deviceExtensionCount) {
            result = VK_INCOMPLETE;
        } else {
            *pPropertyCount = pDesc->deviceExtensionCount;
        }
        for (uint32_t i = 0; i < *pPropertyCount; ++i) {
            pProperties[i] = pDesc->pDeviceExtensions[i];
        }
    }
    return result;
}
'''


class Log():
    def f(msg):
        print('FATAL: ' + msg)
        raise Exception(msg)

    def e(msg):
        print('ERROR: ' + msg)

    def w(msg):
        print('WARNING: ' + msg)

    def i(msg):
        print(msg)


class VulkanPlatform():
    def __init__(self, data):
        self.name = data.get('name')
        self.protect = data.get('protect')


class VulkanStructMember():
    def __init__(self, name, type, limittype, isArray = False):
        self.name = name
        self.type = type
        self.limittype = limittype
        self.isArray = isArray


class VulkanStruct():
    def __init__(self, name):
        self.name = name
        self.sType = None
        self.extends = []
        self.members = dict()
        self.aliases = [ name ]
        self.definedByVersion = None
        self.definedByExtensions = []


class VulkanDefinitionScope():
    def parseAliases(self, xml):
        self.sTypeAliases = dict()
        for sTypeAlias in xml.findall("./require/enum[@alias]"):
            if re.search(r'^VK_STRUCTURE_TYPE_.*', sTypeAlias.get('name')):
                self.sTypeAliases[sTypeAlias.get('alias')] = sTypeAlias.get('name')


class VulkanVersion(VulkanDefinitionScope):
    def __init__(self, xml):
        self.name = xml.get('name')
        self.number = xml.get('number')
        self.parseAliases(xml)


class VulkanExtension(VulkanDefinitionScope):
    def __init__(self, xml, upperCaseName):
        self.name = xml.get('name')
        self.upperCaseName = upperCaseName
        self.type = xml.get('type')
        self.platform = xml.get('platform')
        self.parseAliases(xml)


class VulkanRegistry():
    def __init__(self, registryFile):
        Log.i("Loading registry file: '{0}'".format(registryFile))
        xml = etree.parse(registryFile)
        self.parsePlatformInfo(xml)
        self.parseVersionInfo(xml)
        self.parseExtensionInfo(xml)
        self.parseStructInfo(xml)
        self.parsePrerequisites(xml)
        self.parseAliases(xml)
        self.applyWorkarounds()

    def parsePlatformInfo(self, xml):
        self.platforms = dict()
        for plat in xml.findall("./platforms/platform"):
            self.platforms[plat.get('name')] = VulkanPlatform(plat)


    def parseVersionInfo(self, xml):
        self.versions = dict()
        for feature in xml.findall('./feature'):
            if re.search(r"^[1-9][0-9]*\.[0-9]+$", feature.get('number')):
                self.versions[feature.get('number')] = VulkanVersion(feature)
            else:
                Log.f("Unsupported feature with number '{0}'", feature.get('number'))


    def parseExtensionInfo(self, xml):
        self.extensions = dict()
        for ext in xml.findall("./extensions/extension"):
            # Only care about enabled extensions
            if ext.get('supported') == "vulkan":
                name = ext.get('name')

                # Find name enum (due to inconsistencies in lower case and upper case names this is non-trivial)
                foundNameEnum = False
                matches = ext.findall("./require/enum[@value='\"" + name + "\"']")
                for match in matches:
                    if match.get('name').endswith("_EXTENSION_NAME"):
                        # Add extension definition
                        self.extensions[name] = VulkanExtension(ext, match.get('name')[:-len("_EXTENSION_NAME")])
                        foundNameEnum = True
                        break
                if not foundNameEnum:
                    Log.f("Cannot find name enum for extension '{0}'".format(name))


    def parseStructInfo(self, xml):
        self.structs = dict()
        for struct in xml.findall("./types/type[@category='struct']"):
            # Define base struct information
            structDef = VulkanStruct(struct.get('name'))

            # Find out whether it's an extension structure
            extends = struct.get('structextends')
            if extends != None:
                structDef.extends = extends.split(',')

            # Find sType value
            sType = struct.find("./member[name='sType']")
            if sType != None:
                structDef.sType = sType.get('values')

            # Parse struct members
            for member in struct.findall('./member'):
                name = member.find('./name').text
                tail = member.find('./name').tail
                type = member.find('./type').text

                # Only add real members (skip sType and pNext)
                if name != 'sType' and name != 'pNext':
                    # Define base member information
                    structDef.members[name] = VulkanStructMember(
                        name,
                        type,
                        member.get('limittype')
                    )

                    # Detect if it's an array
                    if tail != None and tail[0] == '[':
                        structDef.members[name].isArray = True

            # Store struct definition
            self.structs[struct.get('name')] = structDef


    def parsePrerequisites(self, xml):
        # Check features (i.e. API versions)
        for feature in xml.findall('./feature'):
            for requireType in feature.findall('./require/type'):
                # Add feature as the source of the definition of a struct
                if requireType.get('name') in self.structs:
                    self.structs[requireType.get('name')].definedByVersion = feature.get('number')

        # Check extensions
        for extension in xml.findall('./extensions/extension'):
            for requireType in extension.findall('./require/type'):
                # Add extension as the source of the definition of a struct
                if requireType.get('name') in self.structs:
                    self.structs[requireType.get('name')].definedByExtensions.append(extension.get('name'))


    def parseAliases(self, xml):
        # Find any struct aliases
        for struct in xml.findall("./types/type[@category='struct']"):
            alias = struct.get('alias')
            if alias != None:
                if alias in self.structs:
                    baseStructDef = self.structs[alias]
                    aliasStructDef = self.structs[struct.get('name')]

                    # Fill missing struct information for the alias
                    aliasStructDef.extends = baseStructDef.extends
                    aliasStructDef.members = baseStructDef.members
                    aliasStructDef.aliases = baseStructDef.aliases
                    aliasStructDef.aliases.append(struct.get('name'))

                    if baseStructDef.sType != None:
                        sTypeAlias = None

                        # First try to find sType alias in core versions
                        if aliasStructDef.definedByVersion != None:
                            for version in self.versions:
                                if version <= aliasStructDef.definedByVersion:
                                    sTypeAlias = self.versions[version].sTypeAliases.get(baseStructDef.sType)
                                    if sTypeAlias != None:
                                        break

                        # Otherwise need to find sType alias in extension
                        if sTypeAlias == None:
                            for extName in aliasStructDef.definedByExtensions:
                                sTypeAlias = self.extensions[extName].sTypeAliases.get(baseStructDef.sType)
                                if sTypeAlias != None:
                                    break

                        if sTypeAlias != None:
                            aliasStructDef.sType = sTypeAlias
                        else:
                            Log.f("Could not find sType enum of alias '{0}' of struct '{1}'".format(alias, struct.get('name')))
                else:
                    Log.f("Failed to find alias '{0}' of struct '{1}'".format(alias, struct.get('name')))


    def applyWorkarounds(self):
        # TODO: We currently have to apply workarounds due to "noauto" limittypes and other bugs related to limittypes in the vk.xml
        # These can only be solved permanently if we make modifications to the registry xml itself
        self.structs['VkPhysicalDeviceLimits'].members['bufferImageGranularity'].limittype = 'min' # should be maxalign
        self.structs['VkPhysicalDeviceLimits'].members['subPixelPrecisionBits'].limittype = 'max'
        self.structs['VkPhysicalDeviceLimits'].members['subTexelPrecisionBits'].limittype = 'max'
        self.structs['VkPhysicalDeviceLimits'].members['mipmapPrecisionBits'].limittype = 'max'
        self.structs['VkPhysicalDeviceLimits'].members['viewportSubPixelBits'].limittype = 'max'
        self.structs['VkPhysicalDeviceLimits'].members['minMemoryMapAlignment'].limittype = 'max' # should be minalign
        self.structs['VkPhysicalDeviceLimits'].members['minTexelBufferOffsetAlignment'].limittype = 'min' # should be maxalign
        self.structs['VkPhysicalDeviceLimits'].members['minUniformBufferOffsetAlignment'].limittype = 'min' # should be maxalign
        self.structs['VkPhysicalDeviceLimits'].members['minStorageBufferOffsetAlignment'].limittype = 'min' # should be maxalign
        self.structs['VkPhysicalDeviceLimits'].members['subPixelInterpolationOffsetBits'].limittype = 'max'
        self.structs['VkPhysicalDeviceLimits'].members['timestampPeriod'].limittype = 'IGNORE' # good question what this should be...
        self.structs['VkPhysicalDeviceLimits'].members['nonCoherentAtomSize'].limittype = 'min' # should be maxalign
        self.structs['VkPhysicalDeviceLimits'].members['maxColorAttachments'].limittype = 'max' # vk.xml declares this with 'bitmask' limittype for some reason
        self.structs['VkPhysicalDeviceLimits'].members['pointSizeGranularity'].limittype = 'min' # should be maxmul
        self.structs['VkPhysicalDeviceLimits'].members['lineWidthGranularity'].limittype = 'min' # should be maxmul
        self.structs['VkPhysicalDeviceVulkan11Properties'].members['subgroupSize'].limittype = 'IGNORE' # good question what this should be...
        self.structs['VkPhysicalDevicePortabilitySubsetPropertiesKHR'].members['minVertexInputBindingStrideAlignment'].limittype = 'min' # should be maxalign

        # TODO: There are also some bugs in the vk.xml, like parameters having "bitmask" limittype but actually VkBool32 type
        # This is non-sense, so we patch them
        for structName in self.structs:
            for memberName in self.structs[structName].members:
                memberDef = self.structs[structName].members[memberName]
                if memberDef.limittype == 'bitmask' and memberDef.type == 'VkBool32':
                    self.structs[structName].members[memberName].limittype = 'noauto'


class VulkanProfileCapabilities():
    def __init__(self, registry, data, caps):
        self.extensions = dict()
        self.instanceExtensions = dict()
        self.deviceExtensions = dict()
        self.features = dict()
        self.properties = dict()
        self.formats = dict()
        self.queueFamiliesProperties = []
        self.memoryProperties = dict()
        for capName in data['capabilities']:
            if capName in caps:
                self.mergeCaps(registry, caps[capName])
            else:
                Log.f("Capability '{0}' needed by profile '{1}' is missing".format(capName, data['name']))


    def mergeCaps(self, registry, caps):
        self.mergeProfileExtensions(registry, caps)
        self.mergeProfileFeatures(caps)
        self.mergeProfileProperties(caps)
        self.mergeProfileFormats(caps)
        self.mergeProfileQueueFamiliesProperties(caps)
        self.mergeProfileMemoryProperties(caps)


    def mergeProfileCapData(self, dst, src):
        if type(src) != type(dst):
            Log.f("Data type confict during profile capability data merge (src is '{0}', dst is '{1}')".format(type(src), type(dst)))
        elif type(src) == dict:
            for key, val in src.items():
                if type(val) == dict:
                    if not key in dst:
                        dst[key] = dict()
                    self.mergeProfileCapData(dst[key], val)

                elif type(val) == list:
                    if not key in dst:
                        dst[key] = []
                    dst[key].extend(val)

                else:
                    if key in dst and type(dst[key]) != type(val):
                        Log.f("Data type confict during profile capability data merge (src is '{0}', dst is '{1}')".format(type(val), type(dst[key])))
                    dst[key] = val
        else:
            Log.f("Unexpected data type during profile capability data merge (src is '{0}', dst is '{1}')".format(type(src), type(dst)))


    def mergeProfileExtensions(self, registry, data):
        if data.get('extensions') != None:
            for extName, specVer in data['extensions'].items():
                extInfo = registry.extensions.get(extName)
                if extInfo != None:
                    self.extensions[extName] = specVer
                    if extInfo.type == 'instance':
                        self.instanceExtensions[extName] = specVer
                    elif extInfo.type == 'device':
                        self.deviceExtensions[extName] = specVer
                    else:
                        Log.f("Extension '{0}' has invalid type '{1}'".format(extName, extInfo.type))
                else:
                    Log.f("Extension '{0}' does not exist".format(extName))


    def mergeProfileFeatures(self, data):
        if data.get('features') != None:
            self.mergeProfileCapData(self.features, data['features'])


    def mergeProfileProperties(self, data):
        if data.get('properties') != None:
            self.mergeProfileCapData(self.properties, data['properties'])


    def mergeProfileFormats(self, data):
        if data.get('formats') != None:
            self.mergeProfileCapData(self.formats, data['formats'])


    def mergeProfileQueueFamiliesProperties(self, data):
        if data.get('queueFamiliesProperties') != None:
            self.queueFamiliesProperties.extend(data['queueFamiliesProperties'])


    def mergeProfileMemoryProperties(self, data):
        if data.get('memoryProperties') != None:
            self.mergeProfileCapData(self.memoryProperties, data['memoryProperties'])


class VulkanProfile():
    def __init__(self, registry, name, data, caps):
        self.name = name
        self.version = data['version']
        self.apiVersion = data['api-version']
        self.fallback = data.get('fallback')
        self.requirements = []
        self.capabilities = VulkanProfileCapabilities(registry, data, caps)
        self.collectCompileTimeRequirements(registry)
        self.validate(registry)


    def collectCompileTimeRequirements(self, registry):
        # Add API version to the list of requirements
        match = re.search(r"^([1-9][0-9]*\.[0-9]+)[^0-9].*$", self.apiVersion)
        if match != None:
            versionNumber = match.group(1)
            if versionNumber in registry.versions:
                self.requirements.append(registry.versions[versionNumber].name)
            else:
                Log.f("No version '{0}' found in registry required by profile '{1}'".format(versionNumber, self.name))
        else:
            Log.f("Invalid version number '{0}' in profile '{1}'".format(self.apiVersion, self.name))

        # Add any required extension to the list of requirements
        for extName in self.capabilities.extensions:
            if extName in registry.extensions:
                self.requirements.append(extName)
            else:
                Log.f("Extension '{0}' required by profile '{1}' does not exist".format(extName, self.name))


    def validate(self, registry):
        self.validateStructDependencies(registry)


    def validateStructDependencies(self, registry):
        for feature in self.capabilities.features:
            self.validateStructDependency(feature, registry)

        for prop in self.capabilities.properties:
            self.validateStructDependency(prop, registry)

        for queueFamilyData in self.capabilities.queueFamiliesProperties:
            for queueFamilyProp in queueFamilyData:
                self.validateStructDependency(queueFamilyProp, registry)

        for memoryProp in self.capabilities.memoryProperties:
            self.validateStructDependency(memoryProp, registry)


    def validateStructDependency(self, structName, registry):
        if structName in registry.structs:
            structDef = registry.structs[structName]
            depFound = False

            # Check if the required API version defines this struct
            if structDef.definedByVersion != None and structDef.definedByVersion <= self.apiVersion:
                depFound = True

            # Check if any required extension defines this struct
            for definedByExtension in structDef.definedByExtensions:
                if definedByExtension in self.capabilities.extensions:
                    depFound = True
                    break

            if not depFound:
                Log.f("Unexpected required struct '{0}' in profile '{1}'".format(structName, self.name))
        else:
            Log.f("Struct '{0}' in profile '{1}' does not exist in the registry".format(structName, self.name))


    def generatePrivateData(self, registry):
        uname = self.name.upper()
        gen = '\n'
        gen += ('#ifdef {0}\n'
                'namespace {1} {{\n').format(self.name, uname)
        gen += self.gen_extensionData(registry, 'instance')
        gen += self.gen_extensionData(registry, 'device')
        gen += ('\n'
                '}} // namespace {0}\n'
                '#endif\n').format(uname)
        return gen

    def gen_extensionData(self, registry, type):
        foundExt = False
        gen = '\n'
        gen += 'static const VkExtensionProperties _{0}Extensions[] = {{\n'.format(type)
        for extName, specVer in self.capabilities.extensions.items():
            extInfo = registry.extensions[extName]
            if extInfo.type == type:
                gen += '    VkExtensionProperties{{ {0}_EXTENSION_NAME, {1} }},\n'.format(extInfo.upperCaseName, specVer)
                foundExt = True
        gen += '};\n'
        return gen if foundExt else ''


class VulkanProfiles():
    def loadFromDir(registry, profilesDir):
        profiles = dict()
        dirAbsPath = os.path.abspath(profilesDir)
        filenames = os.listdir(dirAbsPath)
        for filename in filenames:
            fileAbsPath = os.path.join(dirAbsPath, filename)
            if os.path.isfile(fileAbsPath) and os.path.splitext(filename)[-1] == '.json':
                Log.i("Loading profile file: '{0}'".format(filename))
                with open(fileAbsPath, 'r') as f:
                    jsonData = json.load(f)
                    VulkanProfiles.parseProfiles(registry, profiles, jsonData['profiles'], jsonData['capabilities'])
        return profiles


    def parseProfiles(registry, profiles, json, caps):
        for name, data in json.items():
            Log.i("Registering profile '{0}'".format(name))
            profiles[name] = VulkanProfile(registry, name, data, caps)


class VulkanProfilesBuilder():
    def __init__(self, registry, profiles):
        self.registry = registry
        self.profiles = profiles


    def generate(self, outIncDir, outSrcDir):
        self.generate_h(outIncDir)
        self.generate_cpp(outSrcDir)
        self.generate_hpp(outIncDir)


    def generate_h(self, outDir):
        fileAbsPath = os.path.join(os.path.abspath(outDir), 'vulkan_profiles.h')
        Log.i("Generating '{0}'...".format(fileAbsPath))
        with open(fileAbsPath, 'w') as f:
            f.write(COPYRIGHT_HEADER)
            f.write(H_HEADER)
            f.write(self.gen_profileDefs())
            f.write(API_DEFS)
            f.write(H_FOOTER)


    def generate_cpp(self, outDir):
        fileAbsPath = os.path.join(os.path.abspath(outDir), 'vulkan_profiles.cpp')
        Log.i("Generating '{0}'...".format(fileAbsPath))
        with open(fileAbsPath, 'w') as f:
            f.write(COPYRIGHT_HEADER)
            f.write(CPP_HEADER)
            f.write(self.gen_structPropLists())
            f.write(self.gen_formatLists())
            # TODO: Memory types removed for now
            #f.write(self.gen_memoryTypeLists())
            f.write(self.gen_queueFamilyLists())
            f.write(self.gen_privateImpl())
            f.write(self.gen_publicImpl())


    def generate_hpp(self, outDir):
        fileAbsPath = os.path.join(os.path.abspath(outDir), 'vulkan_profiles.hpp')
        Log.i("Generating '{0}'...".format(fileAbsPath))
        with open(fileAbsPath, 'w') as f:
            f.write(COPYRIGHT_HEADER)
            f.write(HPP_HEADER)
            f.write(self.gen_profileDefs())
            f.write(API_DEFS)
            f.write(self.gen_structPropLists())
            f.write(self.gen_formatLists())
            # TODO: Memory types removed for now
            #f.write(self.gen_memoryTypeLists())
            f.write(self.gen_queueFamilyLists())
            f.write(self.gen_privateImpl())
            f.write(self.gen_publicImpl())
            f.write(HPP_FOOTER)


    def gen_profileDefs(self):
        gen = ''
        for name, profile in self.profiles.items():
            uname = name.upper()
            gen += '\n'

            # Add prerequisites
            if profile.requirements:
                for i, requirement in enumerate(profile.requirements):
                    if i == 0:
                        gen += '#if '
                    else:
                        gen += '    '

                    gen += 'defined({0})'.format(requirement)

                    if i < len(profile.requirements) - 1:
                        gen += ' && \\\n'
                    else:
                        gen += '\n'

            gen += '#define {0} 1\n'.format(name)
            gen += '#define {0}_NAME "{1}"\n'.format(uname, name)
            gen += '#define {0}_SPEC_VERSION {1}\n'.format(uname, profile.version)
            gen += '#define {0}_MIN_API_VERSION VK_MAKE_VERSION({1})\n'.format(uname, profile.apiVersion.replace(".", ", "))

            if profile.requirements:
                gen += '#endif\n'

        return gen


    def gen_privateImpl(self):
        gen = '\n'
        gen += PRIVATE_IMPL_BODY
        gen += self.gen_privateData()
        gen += self.gen_profileDesc()
        return gen


    def gen_privateData(self):
        gen = ''
        for profile in self.profiles.values():
            gen += profile.generatePrivateData(self.registry)
        return gen


    def gen_profileDesc(self):
        gen = '\n'
        gen += 'static const _vpProfileDesc _vpProfiles[] = {\n'

        for name, profile in self.profiles.items():
            uname = name.upper()
            gen += ('#ifdef {0}\n'
                    '    _vpProfileDesc{{\n'
                    '        {1}_NAME,\n'
                    '        {1}_SPEC_VERSION,\n'
                    '        {1}_MIN_API_VERSION,\n').format(name, uname)

            if profile.capabilities.instanceExtensions:
                gen += '        &{0}::_instanceExtensions[0], _vpArraySize({0}::_instanceExtensions),\n'.format(uname)
            else:
                gen += '        nullptr, 0,\n'

            if profile.capabilities.deviceExtensions:
                gen += '        &{0}::_deviceExtensions[0], _vpArraySize({0}::_deviceExtensions)\n'.format(uname)
            else:
                gen += '        nullptr, 0\n'

            gen += ('    },\n'
                    '#endif\n')

        gen += ('    _vpProfileDesc{ nullptr }\n'
                '};\n')
        return gen


    def gen_publicImpl(self):
        gen = PUBLIC_IMPL_BODY
        gen += self.gen_vpGetProfiles()
        gen += self.gen_vpGetProfileFallbacks()
        gen += self.gen_vpGetDeviceProfileSupport()
        gen += self.gen_vpCreateDevice()
        gen += self.gen_vpGetProfileStructures()
        gen += self.gen_vpGetProfileStructureProperties()
        gen += self.gen_vpGetProfileFormats()
        gen += self.gen_vpGetProfileFormatProperties()
        # TODO: Memory types removed for now
        #gen += self.gen_vpGetProfileMemoryTypes()
        gen += self.gen_vpGetProfileQueueFamilies()
        return gen


    def gen_structPropLists(self):
        gen = ''
        for name, profile in self.profiles.items():
            features = profile.capabilities.features
            properties = profile.capabilities.properties
            if features != None or properties != None:
                gen += ('\n'
                        '#ifdef {0}\n'
                        'static const VpStructureProperties _{1}_STRUCTURE_PROPERTIES[] = {{\n').format(name, name.upper())

                if features != None:
                    for featureStructName in features:
                        if featureStructName == 'VkPhysicalDeviceFeatures':
                            # Special case, as it's wrapped into VkPhysicalDeviceFeatures2
                            featureStructName = 'VkPhysicalDeviceFeatures2'

                        structDef = self.registry.structs.get(featureStructName)
                        if structDef == None:
                            Log.f("Feature structure '{0}' does not exist".format(featureStructName))

                        if structDef.sType == None:
                            Log.f("Feature structure '{0}' is not chainable".format(featureStructName))

                        if not 'VkPhysicalDeviceFeatures2' in structDef.extends + [ structDef.name ]:
                            Log.f("Feature structure '{0}' does not extend VkPhysicalDeviceFeatures2".format(featureStructName))

                        gen += '    {{ {0}, VP_STRUCTURE_FEATURES }},\n'.format(structDef.sType)

                if properties != None:
                    for propertyStructName in properties:
                        if propertyStructName == 'VkPhysicalDeviceProperties':
                            # Special case, as it's wrapped into VkPhysicalDeviceProperties2
                            propertyStructName = 'VkPhysicalDeviceProperties2'

                        structDef = self.registry.structs.get(propertyStructName)
                        if structDef == None:
                            Log.f("Properties structure '{0}' does not exist".format(propertyStructName))

                        if structDef.sType == None:
                            Log.f("Properties structure '{0}' is not chainable".format(propertyStructName))

                        if not 'VkPhysicalDeviceProperties2' in [ structDef.name ] + structDef.extends:
                            Log.f("Properties structure '{0}' does not extend VkPhysicalDeviceProperties2".format(propertyStructName))

                        gen += '    {{ {0}, VP_STRUCTURE_PROPERTIES }},\n'.format(structDef.sType)

                gen += ('};\n'
                        '#endif\n')
        return gen


    def gen_formatLists(self):
        gen = '\n'
        # TODO: Make format properties extensible
        gen += ('struct VpFormatProperties {\n'
                '    VkFormat format;\n'
                '    VkFlags64 linearTilingFeatures;\n'
                '    VkFlags64 optimalTilingFeatures;\n'
                '    VkFlags64 bufferFeatures;\n'
                '};\n')
        for name, profile in self.profiles.items():
            if profile.capabilities.formats:
                gen += ('\n'
                        '#ifdef {0}\n'
                        'static const VpFormatProperties _{1}_FORMATS[] = {{\n').format(name, name.upper())
                for format, props in profile.capabilities.formats.items():
                    for propStructName in props:
                        if propStructName != 'VkFormatProperties':
                            Log.f("Unsupported format properties structure '{0}'".format(propStructName))

                    formatProps = props['VkFormatProperties']

                    gen += ('    {{\n'
                            '        {0},\n'
                            '        {1},\n'
                            '        {2},\n'
                            '        {3},\n'
                            '    }},\n').format(format,
                                                self.gen_listValue(formatProps.get('linearTilingFeatures')),
                                                self.gen_listValue(formatProps.get('optimalTilingFeatures')),
                                                self.gen_listValue(formatProps.get('bufferFeatures')))
                gen += ('};\n'
                        '#endif\n')
        return gen


    def gen_memoryTypeLists(self):
        gen = ''
        # TODO: Make memory properties extensible if necessary
        for name, profile in self.profiles.items():
            if profile.capabilities.memoryProperties:
                gen += ('\n'
                        '#ifdef {0}\n'
                        'static const VkMemoryPropertyFlags _{1}_MEMORY_TYPES[] = {{\n').format(name, name.upper())
                for propStructName, members in profile.capabilities.memoryProperties.items():
                    if propStructName != 'VkPhysicalDeviceMemoryProperties':
                        Log.f("Unsupported memory properties structure '{0}'".format(propStructName))
                    for member in members:
                        if member != 'memoryTypes':
                            Log.f("Unsupported memory properties struct member '{0}'".format(member))

                    memoryTypes = members['memoryTypes']
                    for memoryType in memoryTypes:
                        gen += '    {0},\n'.format(self.gen_listValue(memoryType['propertyFlags']))
                gen += ('};\n'
                        '#endif\n')
        return gen


    def gen_queueFamilyLists(self):
        gen = ''
        # TODO: Make queue family properties extensible
        for name, profile in self.profiles.items():
            if profile.capabilities.queueFamiliesProperties:
                gen += ('\n'
                        '#ifdef {0}\n'
                        'static const VkQueueFamilyProperties _{1}_QUEUE_FAMILY_PROPERTIES[] = {{\n').format(name, name.upper())

                for queueFamilyData in profile.capabilities.queueFamiliesProperties:
                    for propStructName, members in queueFamilyData.items():
                        if propStructName != 'VkQueueFamilyProperties':
                            Log.f("Unsupported memory properties structure '{0}'".format(propStructName))

                        gen += '    {0},\n'.format(
                            self.gen_listValue(
                                [
                                    self.gen_listValue(members['queueFlags']),
                                    members['queueCount'],
                                    members['timestampValidBits'],
                                    self.gen_listValue(
                                        [
                                            members['minImageTransferGranularity']['width'],
                                            members['minImageTransferGranularity']['height'],
                                            members['minImageTransferGranularity']['depth']
                                        ], False)
                                ], False))

                gen += ('};\n'
                        '#endif\n')
        return gen


    def gen_vpGetProfiles(self):
        gen = '\n'
        gen += ('VPAPI_ATTR VkResult vpGetProfiles(uint32_t *pPropertyCount, VpProfileProperties *pProperties) {\n'
                '    VkResult result = VK_SUCCESS;\n'
                '    static const VpProfileProperties profiles[] = {\n')

        for name, profile in self.profiles.items():
            gen += ('#ifdef {0}\n'
                    '        {{ {1}_NAME, {1}_SPEC_VERSION }},\n'
                    '#endif\n').format(name, name.upper())

        gen += ('    };\n'
                '\n'
                '    if (pProperties == nullptr) {\n'
                '        *pPropertyCount = _vpArraySize(profiles);\n'
                '    } else {\n'
                '        if (*pPropertyCount < _vpArraySize(profiles)) {\n'
                '            result = VK_INCOMPLETE;\n'
                '        } else {\n'
                '            *pPropertyCount = _vpArraySize(profiles);\n'
                '        }\n'
                '        for (uint32_t i = 0; i < *pPropertyCount; ++i) {\n'
                '            pProperties[i] = profiles[i];\n'
                '        }\n'
                '    }\n'
                '    return result;\n'
                '}\n')
        return gen


    def gen_vpGetProfileFallbacks(self):
        gen = '\n'
        gen += ('VPAPI_ATTR VkResult vpGetProfileFallbacks(const VpProfileProperties *pProfile, uint32_t *pPropertyCount, VpProfileProperties *pProperties) {\n'
                '    VkResult result = VK_SUCCESS;\n')

        for name, profile in self.profiles.items():
            uname = name.upper()
            if profile.fallback:
                gen += ('#ifdef {0}\n'
                        '    if (strcmp(pProfile->profileName, {1}_NAME) == 0) {{\n'
                        '        static const VpProfileProperties {1}_fallbacks[] = {{\n').format(name, uname)
                for fallback in profile.fallback:
                    gen += '            {{ {0}_NAME, {0}_SPEC_VERSION }},\n'.format(fallback.upper())
                gen += ('        }};\n'
                        '\n'
                        '        if (pProperties == nullptr) {{\n'
                        '            *pPropertyCount = _vpArraySize({0}_fallbacks);\n'
                        '        }} else {{\n'
                        '            if (*pPropertyCount < _vpArraySize({0}_fallbacks)) {{\n'
                        '                result = VK_INCOMPLETE;\n'
                        '            }} else {{\n'
                        '                *pPropertyCount = _vpArraySize({0}_fallbacks);\n'
                        '            }}\n'
                        '            for (uint32_t i = 0; i < *pPropertyCount; ++i) {{\n'
                        '                pProperties[i] = {0}_fallbacks[i];\n'
                        '            }}\n'
                        '        }}\n'
                        '    }} else\n').format(uname)
                gen += '#endif\n'

        gen += ('    {\n'
                '        *pPropertyCount = 0;\n'
                '    }\n'
                '    return result;\n'
                '}\n')
        return gen


    def gen_vpGetDeviceProfileSupport(self):
        gen = '\n'
        gen += ('VPAPI_ATTR VkResult vpGetDeviceProfileSupport(VkPhysicalDevice physicalDevice, const VpProfileProperties *pProfile, VkBool32 *pSupported) {\n'
                '    assert(pProfile != nullptr);\n'
                '    assert(pSupported != nullptr);\n'
                '    assert(physicalDevice != VK_NULL_HANDLE);\n'
                '\n'
                '    VkResult result = VK_SUCCESS;\n'
                '\n'
                '    uint32_t extCount;\n'
                '    result = vkEnumerateDeviceExtensionProperties(physicalDevice, nullptr, &extCount, nullptr);\n'
                '    if (result != VK_SUCCESS) return result;\n'
                '    std::vector<VkExtensionProperties> ext(extCount);\n'
                '    result = vkEnumerateDeviceExtensionProperties(physicalDevice, nullptr, &extCount, ext.data());\n'
                '    if (result != VK_SUCCESS) return result;\n'
                '\n'
                '    VkPhysicalDeviceProperties devProps;\n'
                '    vkGetPhysicalDeviceProperties(physicalDevice, &devProps);\n'
                '\n'
                '    *pSupported = VK_FALSE;\n'
                '\n')

        for name, profile in self.profiles.items():
            uname = name.upper()
            gen += ('#ifdef {0}\n'
                    '    if (strcmp(pProfile->profileName, {1}_NAME) == 0) {{\n'
                    '        if ({1}_SPEC_VERSION < pProfile->specVersion) return result;\n'
                    '\n'
                    '        if (VK_VERSION_PATCH(devProps.apiVersion) < VK_VERSION_PATCH({1}_MIN_API_VERSION)) return result;\n').format(name, uname)

            if profile.capabilities.deviceExtensions:
                gen += ('\n'
                        '        for (uint32_t i = 0; i < _vpArraySize({0}::_deviceExtensions); ++i) {{\n'
                        '            if (!_vpCheckExtension(ext.data(), ext.size(), {0}::_deviceExtensions[i].extensionName)) return result;\n'
                        '        }}\n').format(uname)

            # Check features
            features = profile.capabilities.features
            if features:
                pNextDevice = None
                pNextProfile = None
                gen += '\n'
                genDef = ''
                genCheck = '        bool featuresSupported = true;\n'
                for featureStructName, feature in features.items():
                    structDef = self.registry.structs.get(featureStructName)
                    if structDef == None:
                        Log.f("Feature structure '{0}' does not exist".format(featureStructName))

                    if featureStructName == 'VkPhysicalDeviceFeatures':
                        # Special case, as it's wrapped into VkPhysicalDeviceFeatures2
                        featureStructName = 'VkPhysicalDeviceFeatures2'
                        varAccessSuffix = '.features.'
                        sType = 'VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2'
                    else:
                        varAccessSuffix = '.'
                        sType = structDef.sType

                    deviceVarName = 'device' + featureStructName[2:]
                    genDef += '        {0} {1}{{ {2} }};\n'.format(featureStructName, deviceVarName, sType)
                    if featureStructName != 'VkPhysicalDeviceFeatures2':
                        if pNextDevice != None:
                            genDef += '        {0}.pNext = &{1};\n'.format(deviceVarName, pNextDevice)
                        pNextDevice = deviceVarName

                    profileVarName = 'profile' + featureStructName[2:]
                    genDef += '        {0} {1}{{ {2} }};\n'.format(featureStructName, profileVarName, sType)
                    if pNextProfile != None:
                        genDef += '        {0}.pNext = &{1};\n'.format(profileVarName, pNextProfile)
                    pNextProfile = profileVarName

                    genCheck += self.gen_compareStructVar('        featuresSupported = featuresSupported && {0};\n', structDef, deviceVarName + varAccessSuffix, profileVarName + varAccessSuffix, feature)

                genCheck = genCheck[:-1] + ';\n'

                if not 'VkPhysicalDeviceFeatures' in features and not 'VkPhysicalDeviceFeatures2' in features:
                    # We have to manually add VkPhysicalDeviceFeatures2 as it's not used in the profile
                    genDef += '        VkPhysicalDeviceFeatures2 devicePhysicalDeviceFeatures2{ VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2 };\n'
                if pNextDevice != None:
                    # For vkGetPhysicalDeviceFeatures2 everything has to be chained to VkPhysicalDeviceFeatures2
                    genDef += '        devicePhysicalDeviceFeatures2.pNext = &{0};\n'.format(pNextDevice)

                gen += genDef
                gen += '        vkGetPhysicalDeviceFeatures2(physicalDevice, &devicePhysicalDeviceFeatures2);\n'
                gen += '        vpGetProfileStructures(pProfile, &{0});\n'.format(pNextProfile)
                gen += genCheck
                gen += '        if (!featuresSupported) return result;\n'

            # Check properties
            properties = profile.capabilities.properties
            if properties:
                pNextDevice = None
                pNextProfile = None
                gen += '\n'
                genDef = ''
                genCheck = '        bool propertiesSupported = true;\n'
                for propertyStructName, property in properties.items():
                    structDef = self.registry.structs.get(propertyStructName)
                    if structDef == None:
                        Log.f("Properties structure '{0}' does not exist".format(propertyStructName))

                    if propertyStructName == 'VkPhysicalDeviceProperties':
                        # Special case, as it's wrapped into VkPhysicalDeviceProperties2
                        propertyStructName = 'VkPhysicalDeviceProperties2'
                        varAccessSuffix = '.properties.'
                        sType = 'VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2'
                    else:
                        varAccessSuffix = '.'
                        sType = structDef.sType

                    deviceVarName = 'device' + propertyStructName[2:]
                    genDef += '        {0} {1}{{ {2} }};\n'.format(propertyStructName, deviceVarName, sType)
                    if propertyStructName != 'VkPhysicalDeviceProperties2':
                        if pNextDevice != None:
                            genDef += '        {0}.pNext = &{1};\n'.format(deviceVarName, pNextDevice)
                        pNextDevice = deviceVarName

                    profileVarName = 'profile' + propertyStructName[2:]
                    genDef += '        {0} {1}{{ {2} }};\n'.format(propertyStructName, profileVarName, sType)
                    if pNextProfile != None:
                        genDef += '        {0}.pNext = &{1};\n'.format(profileVarName, pNextProfile)
                    pNextProfile = profileVarName

                    genCheck += self.gen_compareStructVar('        propertiesSupported = propertiesSupported && {0};\n', structDef, deviceVarName + varAccessSuffix, profileVarName + varAccessSuffix, property)

                genCheck = genCheck[:-1] + ';\n'

                if not 'VkPhysicalDeviceProperties' in properties and not 'VkPhysicalDeviceProperties2' in properties:
                    # We have to manually add VkPhysicalDeviceProperies2 as it's not used in the profile
                    genDef += '        VkPhysicalDeviceProperties2 devicePhysicalDeviceProperties2{ VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2 };\n'
                if pNextDevice != None:
                    # For vkGetPhysicalDeviceProperties2 everything has to be chained to VkPhysicalDeviceProperties2
                    genDef += '        devicePhysicalDeviceProperties2.pNext = &{0};\n'.format(pNextDevice)

                gen += genDef
                gen += '        vkGetPhysicalDeviceProperties2(physicalDevice, &devicePhysicalDeviceProperties2);\n'
                gen += '        vpGetProfileStructures(pProfile, &{0});\n'.format(pNextProfile)
                gen += genCheck
                gen += '        if (!propertiesSupported) return result;\n'

            # Check queue family properties
            if profile.capabilities.queueFamiliesProperties:
                gen += ('\n'
                        '        uint32_t queueFamilyCount = 0;\n'
                        '        vkGetPhysicalDeviceQueueFamilyProperties(physicalDevice, &queueFamilyCount, nullptr);\n'
                        '        std::vector<VkQueueFamilyProperties> queueFamilies(queueFamilyCount);\n'
                        '        vkGetPhysicalDeviceQueueFamilyProperties(physicalDevice, &queueFamilyCount, queueFamilies.data());\n'
                        '\n'
                        '        bool queueFamiliesSupported = true;\n'
                        '        for (uint32_t i = 0; i < _vpArraySize(_{0}_QUEUE_FAMILY_PROPERTIES); ++i) {{\n'
                        '            if (!_vpCheckQueueFamilyProperty(&queueFamilies[0], queueFamilyCount, _{0}_QUEUE_FAMILY_PROPERTIES[i])) {{\n'
                        '                queueFamiliesSupported = false;\n'
                        '                break;\n'
                        '            }}\n'
                        '        }}\n'
                        '        if (!queueFamiliesSupported) return result;\n').format(uname)

            # Check memory types
            if profile.capabilities.memoryProperties:
                gen += ('\n'
                        '        VkPhysicalDeviceMemoryProperties memoryProperties;\n'
                        '        vkGetPhysicalDeviceMemoryProperties(physicalDevice, &memoryProperties);\n'
                        '\n'
                        '        bool memoryTypesSupported = true;\n'
                        '        for (uint32_t i = 0; i < _vpArraySize(_{0}_MEMORY_TYPES); ++i) {{\n'
                        '            if (!_vpCheckMemoryProperty(memoryProperties, _{0}_MEMORY_TYPES[i])) {{\n'
                        '                memoryTypesSupported = false;\n'
                        '                break;\n'
                        '            }}\n'
                        '        }}\n'
                        '        if (!memoryTypesSupported) return result;\n').format(uname)

            gen += ('    } else\n'
                    '#endif\n')

        gen += ('    {\n'
                '        return result;\n'
                '    }\n'
                '\n'
                '    *pSupported = VK_TRUE;\n'
                '    return result;\n'
                '}\n')
        return gen


    def gen_vpCreateDevice(self):
        gen = '\n'
        gen += ('VPAPI_ATTR VkResult vpCreateDevice(VkPhysicalDevice physicalDevice, const VpDeviceCreateInfo *pCreateInfo,\n'
                '                                   const VkAllocationCallbacks *pAllocator, VkDevice *pDevice) {\n'
                '    assert(pCreateInfo != nullptr);\n'
                '\n'
                '    if (physicalDevice == VK_NULL_HANDLE || pCreateInfo == nullptr || pDevice == nullptr) {\n'
                '        return vkCreateDevice(physicalDevice, pCreateInfo == nullptr ? nullptr : pCreateInfo->pCreateInfo, pAllocator, pDevice);\n'
                '    } else if (pCreateInfo->pProfile == nullptr || strcmp(pCreateInfo->pProfile->profileName, "") == 0) {\n'
                '        return vkCreateDevice(physicalDevice, pCreateInfo->pCreateInfo, pAllocator, pDevice);\n'
                '    } else\n')

        for name, profile in self.profiles.items():
            uname = name.upper()

            # TODO: Well, this is bogus now, as we add all extensions here even though some may be instance
            # and not device extensions, but we'll keep it as is for now to maintain existing behavior
            gen += ('#ifdef {0}\n'
                    '    if (strcmp(pCreateInfo->pProfile->profileName, {1}_NAME) == 0) {{\n'
                    '        std::vector<const char*> extensions;\n'
                    '        _vpGetDeviceExtensions(pCreateInfo, _vpArraySize({1}::_deviceExtensions), &{1}::_deviceExtensions[0], extensions);\n'
                    '\n'
                    '        void *pNext = const_cast<void*>(pCreateInfo->pCreateInfo->pNext);\n').format(name, uname)

            # Add profile feature structures if they aren't overridden by application
            features = profile.capabilities.features
            if features:
                genDef = ''
                genCheck = ''
                pNext = None
                for featureStructName, feature in features.items():
                    structDef = self.registry.structs.get(featureStructName)
                    if structDef == None:
                        Log.f("Feature structure '{0}' does not exist".format(featureStructName))

                    if featureStructName == 'VkPhysicalDeviceFeatures':
                        # Special case, as it's wrapped into VkPhysicalDeviceFeatures2
                        featureStructName = 'VkPhysicalDeviceFeatures2'
                        sType = 'VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2'
                    else:
                        sType = structDef.sType

                    profileVarName = 'profile' + featureStructName[2:]
                    genDef += '        {0} {1}{{ {2} }};\n'.format(featureStructName, profileVarName, sType)
                    if pNext != None:
                        genDef += '        {0}.pNext = &{1};\n'.format(profileVarName, pNext)
                    pNext = profileVarName

                    if featureStructName == 'VkPhysicalDeviceFeatures2':
                        genCheck += ('        if (pCreateInfo->pCreateInfo->pEnabledFeatures != nullptr) {{\n'
                                     '            profilePhysicalDeviceFeatures2.features = *pCreateInfo->pCreateInfo->pEnabledFeatures;\n'
                                     '        }}\n'
                                     '        if (pCreateInfo->flags & VP_DEVICE_CREATE_DISABLE_ROBUST_BUFFER_ACCESS_BIT) {{\n'
                                     '            profilePhysicalDeviceFeatures2.features.robustBufferAccess = VK_FALSE;\n'
                                     '        }}\n'
                                     '        if (_vpGetStructure(pNext, {0}) == nullptr && pCreateInfo->pCreateInfo->pEnabledFeatures == nullptr) {{\n').format(sType)
                    else:
                        if featureStructName == 'VkPhysicalDeviceVulkan13Features':
                            genCheck += ('        if (pCreateInfo->flags & VP_DEVICE_CREATE_DISABLE_ROBUST_IMAGE_ACCESS_BIT) {\n'
                                         '            profilePhysicalDeviceVulkan13Features.robustImageAccess = VK_FALSE;\n'
                                         '        }\n')
                        genCheck += '        if (_vpGetStructure(pNext, {0}) == nullptr) {{\n'.format(sType)
                    genCheck += ('            {0}.pNext = pNext;\n'
                                 '            pNext = &{0};\n'
                                 '        }}\n').format(profileVarName)

                gen += genDef
                gen += '        vpGetProfileStructures(pCreateInfo->pProfile, &{0});\n'.format(pNext)
                gen += genCheck

            gen += ('\n'
                    '        VkDeviceCreateInfo deviceCreateInfo{ VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO };\n'
                    '        deviceCreateInfo.pNext = pNext;\n'
                    '        deviceCreateInfo.flags = pCreateInfo->pCreateInfo->flags;\n'
                    '        deviceCreateInfo.queueCreateInfoCount = pCreateInfo->pCreateInfo->queueCreateInfoCount;\n'
                    '        deviceCreateInfo.pQueueCreateInfos = pCreateInfo->pCreateInfo->pQueueCreateInfos;\n'
                    '        deviceCreateInfo.enabledExtensionCount = static_cast<uint32_t>(extensions.size());\n'
                    '        deviceCreateInfo.ppEnabledExtensionNames = extensions.data();\n')

            if not 'VkPhysicalDeviceFeatures' in features and not 'VkPhysicalDeviceFeatures2' in features:
                gen += ('        VkPhysicalDeviceFeatures enabledFeatures;\n'
                        '        if (pCreateInfo->pCreateInfo->pEnabledFeatures != nullptr) {\n'
                        '            enabledFeatures = *pCreateInfo->pCreateInfo->pEnabledFeatures;\n'
                        '            if (pCreateInfo->flags & VP_DEVICE_CREATE_DISABLE_ROBUST_BUFFER_ACCESS_BIT) {\n'
                        '                enabledFeatures.robustBufferAccess = VK_FALSE;\n'
                        '            }\n'
                        '            deviceCreateInfo.pEnabledFeatures = &enabledFeatures;\n'
                        '        }\n')

            gen += ('        return vkCreateDevice(physicalDevice, &deviceCreateInfo, pAllocator, pDevice);\n'
                    '    } else\n'
                    '#endif\n')

        gen += ('    {\n'
                '        return VK_ERROR_UNKNOWN;\n'
                '    }\n'
                '}\n')
        return gen


    def gen_listValue(self, values, isEnum = True):
        gen = ''
        if not isEnum:
            gen += '{ '

        separator = ''
        if values != None and len(values) > 0:
            for value in values:
                gen += separator + str(value)
                if isEnum:
                    separator = ' | '
                else:
                    separator = ', '
        elif isEnum:
            gen += '0'

        if not isEnum:
            gen += ' }'
        return gen


    def gen_assignStructVar(self, structDef, var, values):
        gen = ''
        for member, value in values.items():
            if member in structDef.members:
                if type(value) == dict:
                    # Nested structure
                    memberDef = self.registry.structs.get(structDef.members[member].type)
                    if memberDef != None:
                        gen += self.gen_assignStructVar(memberDef, var + member + '.', value)
                    else:
                        Log.f("Member '{0}' in structure '{1}' is not a struct".format(member, structDef.name))

                elif type(value) == list:
                    # Some sort of list (enums or integer/float list for structure initialization)
                    if structDef.members[member].isArray:
                        # If it's an array we have to generate per-element assignment code
                        for i, v in enumerate(value):
                            gen += '{0}{1}[{2}] = {3};\n'.format(var, member, i, v)
                    else:
                        # For enums and struct initialization, most of the code can be shared
                        gen += '{0}{1} = '.format(var, member)
                        isEnum = isinstance(value[0], str)
                        gen += '{0};\n'.format(self.gen_listValue(value, isEnum))

                elif type(value) == bool:
                    # Boolean
                    gen += '{0}{1} = {2};\n'.format(var, member, 'VK_TRUE' if value else 'VK_FALSE')

                else:
                    # Everything else
                    gen += '{0}{1} = {2};\n'.format(var, member, value)
            else:
                Log.f("No member '{0}' in structure '{1}'".format(member, structDef.name))
        return gen


    def gen_compareStructVar(self, fmt, structDef, deviceVar, profileVar, values):
        gen = ''
        for member, value in values.items():
            if member in structDef.members:
                limittype = structDef.members[member].limittype
                if limittype == 'IGNORE':
                    # Skip this member as we don't know how to validate it
                    continue
                if limittype == 'bitmask':
                    # Compare bitmask by checking if device value contains every bit of profile value
                    comparePredFmt = '(({0} & {1}) == {1})'
                elif limittype == 'max':
                    # Compare max limit by checking if device value is greater than or equal to profile value
                    comparePredFmt = '({0} >= {1})'
                elif limittype == 'min':
                    # Compare min limit by checking if device value is less than or equal to profile value
                    comparePredFmt = '({0} <= {1})'
                elif limittype == 'range':
                    # Compare range limit by checking if device range is larger than or equal to profile range
                    comparePredFmt = [ '({0} <= {1})', '({0} >= {1})' ]
                elif limittype is None or limittype == 'noauto' or limittype == 'struct':
                    # Compare everything else with equality
                    comparePredFmt = '({0} == {1})'
                else:
                    Log.f("Unsupported limittype '{0}' in member '{1}' of structure '{2}'".format(limittype, member, structDef.name))

                if type(value) == dict:
                    # Nested structure
                    memberDef = self.registry.structs.get(structDef.members[member].type)
                    if memberDef != None:
                        gen += self.gen_compareStructVar(fmt, memberDef, deviceVar + member + '.', profileVar + member + '.', value)
                    else:
                        Log.f("Member '{0}' in structure '{1}' is not a struct".format(member, structDef.name))

                elif type(value) == list:
                    # Some sort of list (enums or integer/float list for structure initialization)
                    if structDef.members[member].isArray:
                        # If it's an array we have to generate per-element comparison code
                        for i in range(len(value)):
                            if limittype == 'range':
                                gen += fmt.format(comparePredFmt[i].format('{0}{1}[{2}]'.format(deviceVar, member, i),
                                                                           '{0}{1}[{2}]'.format(profileVar, member, i)))
                            else:
                                gen += fmt.format(comparePredFmt.format('{0}{1}[{2}]'.format(deviceVar, member, i),
                                                                        '{0}{1}[{2}]'.format(profileVar, member, i)))
                    else:
                        # Enum flags and basic structs can be compared directly
                        gen += fmt.format(comparePredFmt.format('{0}{1}'.format(deviceVar, member),
                                                                '{0}{1}'.format(profileVar, member)))

                else:
                    # Everything else
                    gen += fmt.format(comparePredFmt.format('{0}{1}'.format(deviceVar, member),
                                                            '{0}{1}'.format(profileVar, member)))
            else:
                Log.f("No member '{0}' in structure '{1}'".format(member, structDef.name))
        return gen


    def gen_vpGetProfileStructures(self):
        gen = '\n'
        gen += ('VPAPI_ATTR void vpGetProfileStructures(const VpProfileProperties *pProfile, void *pNext) {\n'
                '    if (pProfile == nullptr || pNext == nullptr) return;\n'
                '    VkBaseOutStructure* p = static_cast<VkBaseOutStructure*>(pNext);\n')

        for name, profile in self.profiles.items():
            uname = name.upper()
            gen += ('#ifdef {0}\n'
                    '    if (strcmp(pProfile->profileName, {1}_NAME) == 0) {{\n'
                    '        while (p != nullptr) {{\n'
                    '            switch (p->sType) {{\n').format(name, uname)

            # Generate feature structure data
            features = profile.capabilities.features
            if features:
                for featureStructName in features:
                    structDef = self.registry.structs.get(featureStructName)
                    if structDef == None:
                        Log.f("Feature structure '{0}' does not exist".format(featureStructName))

                    if featureStructName == 'VkPhysicalDeviceFeatures':
                        # Special case, as it's wrapped into VkPhysicalDeviceFeatures2
                        gen += ('                case VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2: {\n'
                                '                    VkPhysicalDeviceFeatures2* wrap = reinterpret_cast<VkPhysicalDeviceFeatures2*>(p);\n'
                                '                    VkPhysicalDeviceFeatures* features = &wrap->features;\n')
                    elif structDef.sType:
                        gen += '                case {0}: {{\n'.format(structDef.sType)
                        gen += '                    {0}* features = reinterpret_cast<{0}*>(p);\n'.format(featureStructName)
                    else:
                        Log.f("Feature structure '{0}' is not chainable".format(featureStructName))

                    gen += self.gen_assignStructVar(structDef, '                    features->', features[featureStructName])
                    gen += '                } break;\n'

            # Generate property structure data
            properties = profile.capabilities.properties
            if properties:
                for propertyStructName in properties:
                    structDef = self.registry.structs.get(propertyStructName)
                    if structDef == None:
                        Log.f("Properties structure '{0}' does not exist".format(propertyStructName))

                    if propertyStructName == 'VkPhysicalDeviceProperties':
                        # Special case, as it's wrapped into VkPhysicalDeviceProperties2
                        gen += ('                case VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2: {\n'
                                '                    VkPhysicalDeviceProperties2* wrap = reinterpret_cast<VkPhysicalDeviceProperties2*>(p);\n'
                                '                    VkPhysicalDeviceProperties* props = &wrap->properties;\n')
                    elif structDef.sType:
                        gen += '                case {0}: {{\n'.format(structDef.sType)
                        gen += '                    {0}* props = reinterpret_cast<{0}*>(p);\n'.format(propertyStructName)
                    else:
                        Log.f("Properties structure '{0}' is not chainable".format(propertyStructName))

                    gen += self.gen_assignStructVar(structDef, '                    props->', properties[propertyStructName])
                    gen += '                } break;\n'

            gen += ('                default: break;\n'
                    '            }\n'
                    '            p = p->pNext;\n'
                    '        }\n'
                    '    } else\n'
                    '#endif\n')

        gen += ('    {\n'
                '    }\n'
                '}\n')
        return gen


    def gen_vpGetProfileStructureProperties(self):
        gen = '\n'
        gen += ('VPAPI_ATTR VkResult vpGetProfileStructureProperties(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,\n'
                '                                                    VpStructureProperties *pProperties) {\n'
                '    VkResult result = VK_SUCCESS;\n')

        for name, profile in self.profiles.items():
            if profile.capabilities.features or profile.capabilities.properties:
                gen += ('#ifdef {0}\n'
                        '    if (strcmp(pProfile->profileName, {1}_NAME) == 0) {{\n'
                        '        if (pProperties == nullptr) {{\n'
                        '            *pPropertyCount = _vpArraySize(_{1}_STRUCTURE_PROPERTIES);\n'
                        '        }} else {{\n'
                        '            if (*pPropertyCount < _vpArraySize(_{1}_STRUCTURE_PROPERTIES)) {{\n'
                        '                result = VK_INCOMPLETE;\n'
                        '            }} else {{\n'
                        '                *pPropertyCount = _vpArraySize(_{1}_STRUCTURE_PROPERTIES);\n'
                        '            }}\n'
                        '            for (uint32_t i = 0; i < *pPropertyCount; ++i) {{\n'
                        '                pProperties[i] = _{1}_STRUCTURE_PROPERTIES[i];\n'
                        '            }}\n'
                        '        }}\n'
                        '    }} else\n'
                        '#endif\n').format(name, name.upper())

        gen += ('    {\n'
                '        *pPropertyCount = 0;\n'
                '    }\n'
                '    return result;\n'
                '}\n')
        return gen


    def gen_vpGetProfileFormats(self):
        gen = '\n'
        gen += ('VPAPI_ATTR VkResult vpGetProfileFormats(const VpProfileProperties *pProfile, uint32_t *pFormatCount, VkFormat *pFormats) {\n'
                '    VkResult result = VK_SUCCESS;\n')

        for name, profile in self.profiles.items():
            if profile.capabilities.formats:
                gen += ('#ifdef {0}\n'
                        '    if (strcmp(pProfile->profileName, {1}_NAME) == 0) {{\n'
                        '        if (pFormats == nullptr) {{\n'
                        '            *pFormatCount = _vpArraySize(_{1}_FORMATS);\n'
                        '        }} else {{\n'
                        '            if (*pFormatCount < _vpArraySize(_{1}_FORMATS)) {{\n'
                        '                result = VK_INCOMPLETE;\n'
                        '            }} else {{\n'
                        '                *pFormatCount = _vpArraySize(_{1}_FORMATS);\n'
                        '            }}\n'
                        '            for (uint32_t i = 0; i < *pFormatCount; ++i) {{\n'
                        '                pFormats[i] = _{1}_FORMATS[i].format;\n'
                        '            }}\n'
                        '        }}\n'
                        '    }} else\n'
                        '#endif\n').format(name, name.upper())

        gen += ('    {\n'
                '        *pFormatCount = 0;\n'
                '    }\n'
                '    return result;\n'
                '}\n')
        return gen


    def gen_vpGetProfileFormatProperties(self):
        gen = '\n'
        gen += ('VPAPI_ATTR void vpGetProfileFormatProperties(const VpProfileProperties *pProfile, VkFormat format, void *pNext) {\n'
                '    if (pProfile == nullptr || pNext == nullptr) return;\n'
                '    VkBaseOutStructure* p = static_cast<VkBaseOutStructure*>(pNext);\n')

        for name, profile in self.profiles.items():
            if profile.capabilities.formats:
                gen += ('#ifdef {0}\n'
                        '    if (strcmp(pProfile->profileName, {1}_NAME) == 0) {{\n'
                        '        for (uint32_t i = 0; i < _vpArraySize(_{1}_FORMATS); ++i) {{\n'
                        '            const VpFormatProperties& props = _{1}_FORMATS[i];\n'
                        '            if (props.format != format) continue;\n'
                        '\n'
                        '            while (p != nullptr) {{\n'
                        '                switch (p->sType) {{\n').format(name, name.upper())

                # TODO: Make format properties extensible
                formatPropTypes = [
                    {
                        'sType': 'VK_STRUCTURE_TYPE_FORMAT_PROPERTIES_2',
                        'varDecl': 'VkFormatProperties2* pProps = reinterpret_cast<VkFormatProperties2*>(p);',
                        'varRef': 'pProps->formatProperties.',
                        'valCast': 'static_cast<VkFormatFeatureFlags>'
                    },
                    {
                        'sType': 'VK_STRUCTURE_TYPE_FORMAT_PROPERTIES_3_KHR',
                        'varDecl': 'VkFormatProperties3KHR* pProps = reinterpret_cast<VkFormatProperties3KHR*>(p);',
                        'varRef': 'pProps->',
                        'valCast': ''
                    }
                ]
                for types in formatPropTypes:
                    gen += ('                    case {0}: {{\n'
                            '                        {1};\n'
                            '                        {2}linearTilingFeatures = {3}(props.linearTilingFeatures);\n'
                            '                        {2}optimalTilingFeatures = {3}(props.optimalTilingFeatures);\n'
                            '                        {2}bufferFeatures = {3}(props.bufferFeatures);\n'
                            '                    }} break;\n').format(types['sType'], types['varDecl'], types['varRef'], types['valCast'])

                gen += ('                    default: break;\n'
                        '                }\n'
                        '                p = p->pNext;\n'
                        '            }\n'
                        '        }\n'
                        '    } else\n'
                        '#endif\n')

        gen += ('    {\n'
                '    }\n'
                '}\n')
        return gen


    def gen_vpGetProfileMemoryTypes(self):
        gen = '\n'
        gen += ('VPAPI_ATTR VkResult vpGetProfileMemoryTypes(const VpProfileProperties *pProfile, uint32_t *pMemoryPropertyFlagsCount,\n'
                '                                            VkMemoryPropertyFlags *pMemoryPropertyFlags) {\n'
                '    VkResult result = VK_SUCCESS;\n')

        for name, profile in self.profiles.items():
            if profile.capabilities.memoryProperties:
                gen += ('#ifdef {0}\n'
                        '    if (strcmp(pProfile->profileName, {1}_NAME) == 0) {{\n'
                        '        if (pMemoryPropertyFlags == nullptr) {{\n'
                        '            *pMemoryPropertyFlagsCount = _vpArraySize(_{1}_MEMORY_TYPES);\n'
                        '        }} else {{\n'
                        '            if (*pMemoryPropertyFlagsCount < _vpArraySize(_{1}_MEMORY_TYPES)) {{\n'
                        '                result = VK_INCOMPLETE;\n'
                        '            }} else {{\n'
                        '                *pMemoryPropertyFlagsCount = _vpArraySize(_{1}_MEMORY_TYPES);\n'
                        '            }}\n'
                        '            for (uint32_t i = 0; i < *pMemoryPropertyFlagsCount; ++i) {{\n'
                        '                pMemoryPropertyFlags[i] = _{1}_MEMORY_TYPES[i];\n'
                        '            }}\n'
                        '        }}\n'
                        '    }} else\n'
                        '#endif\n').format(name, name.upper())

        gen += ('    {\n'
                '        *pMemoryPropertyFlagsCount = 0;\n'
                '    }\n'
                '    return result;\n'
                '}\n')
        return gen


    def gen_vpGetProfileQueueFamilies(self):
        gen = '\n'
        gen += ('VPAPI_ATTR VkResult vpGetProfileQueueFamilies(const VpProfileProperties *pProfile, uint32_t *pQueueFamilyPropertiesCount,\n'
                '                                              VkQueueFamilyProperties *pQueueFamilyProperties) {\n'
                '    VkResult result = VK_SUCCESS;\n')

        for name, profile in self.profiles.items():
            if profile.capabilities.queueFamiliesProperties:
                gen += ('#ifdef {0}\n'
                        '    if (strcmp(pProfile->profileName, {1}_NAME) == 0) {{\n'
                        '        if (pQueueFamilyProperties == nullptr) {{\n'
                        '            *pQueueFamilyPropertiesCount = _vpArraySize(_{1}_QUEUE_FAMILY_PROPERTIES);\n'
                        '        }} else {{\n'
                        '            if (*pQueueFamilyPropertiesCount < _vpArraySize(_{1}_QUEUE_FAMILY_PROPERTIES)) {{\n'
                        '                result = VK_INCOMPLETE;\n'
                        '            }} else {{\n'
                        '                *pQueueFamilyPropertiesCount = _vpArraySize(_{1}_QUEUE_FAMILY_PROPERTIES);\n'
                        '            }}\n'
                        '            for (uint32_t i = 0; i < *pQueueFamilyPropertiesCount; ++i) {{\n'
                        '                pQueueFamilyProperties[i] = _{1}_QUEUE_FAMILY_PROPERTIES[i];\n'
                        '            }}\n'
                        '        }}\n'
                        '    }} else\n'
                        '#endif\n').format(name, name.upper())

        gen += ('    {\n'
                '        *pQueueFamilyPropertiesCount = 0;\n'
                '    }\n'
                '    return result;\n'
                '}\n')
        return gen


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # TODO: Remove temporary default values used for testing purposes only
    parser.add_argument('-registry', action='store',
                        default='./library/scripts/vk.xml',
                        help='Use specified registry file instead of vk.xml')
    parser.add_argument('-profiles', action='store',
                        default='./profiles',
                        help='Generate based on profiles in the specified directory')
    parser.add_argument('-outIncDir', action='store',
                        default='./library/include/vulkan',
                        help='Output include directory')
    parser.add_argument('-outSrcDir', action='store',
                        default='./library/source',
                        help='Output source directory')

    args = parser.parse_args()

    registry = VulkanRegistry(args.registry)
    profiles = VulkanProfiles.loadFromDir(registry, args.profiles)
    builder = VulkanProfilesBuilder(registry, profiles)
    builder.generate(args.outIncDir, args.outSrcDir)