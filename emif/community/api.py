# -*- coding: utf-8 -*-
# Copyright (C) 2014 Universidade de Aveiro, DETI/IEETA, Bioinformatics Group - http://bioinformatics.ua.pt/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import logging

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import parser_classes
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from developer.serializers import UserSerializer
from models import CommunitiesFavorited, Community, CommunityGroup, CommunityUser, PluginPermission, \
    QuestionSetAccessGroups

logger = logging.getLogger(__name__)


############################################################
##### Checks if a slug is free - Web service
############################################################


class CommunityFreeSlugView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, slug):

        if request.user.is_authenticated():

            free=True

            #print slug

            try:
                c = Community.objects.get(slug=slug)
                free = False
            except Community.DoesNotExist:
                pass

            return Response({'free': free}, status=status.HTTP_200_OK)

        return  Response({}, status=status.HTTP_403_FORBIDDEN)


############################################################
##### Makes a user leave a community - Web service
############################################################


class CommunityLeaveView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, community):

        if request.user.is_authenticated():

            try:
                cu = CommunityUser.objects.get(community__slug=community, user=request.user)

                cu.delete()

                return Response({'success': True}, status=status.HTTP_200_OK)

            except CommunityUser.DoesNotExist:
                pass

        return  Response({}, status=status.HTTP_403_FORBIDDEN)

############################################################
##### Makes a user favorite a community - Web service
############################################################

class CommunityFavoriteView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, community):

        if request.user.is_authenticated():

            try:
                c = Community.objects.get(slug=community)
                cf = CommunitiesFavorited(community=c, user=request.user)
                cf.save()

                return Response({'success': True}, status=status.HTTP_200_OK)

            except CommunitiesFavorited.DoesNotExist:
                pass

        return  Response({}, status=status.HTTP_403_FORBIDDEN)

class CommunityUnfavoriteView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, community):

        if request.user.is_authenticated():

            try:
                c = Community.objects.get(slug=community)
                cf = CommunitiesFavorited.objects.get(community=c, user=request.user)
                
                cf.delete()


            except CommunityUser.DoesNotExist:
                pass

        return Response({'success': True}, status=status.HTTP_200_OK)

############################################################
##### Get list of users belonging to a community group - Web service
############################################################


class CommunityGroupView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, community, group):

        if request.user.is_authenticated():
            try:
            
                # This variable name rocks :D 
                cu = CommunityUser.objects.get(community__slug=community, user=request.user)
                #print cu.user
                #print cu.community
                try:
                    cuin = cu.community.owners.all().get(id=request.user.id)

                    try:
                        cg = CommunityGroup.valid(community = cu.community).get(id=int(group))
                        members = cg.members.all()
                        cus = CommunityUser.objects.filter(community__slug=community)

                        possible = cus.exclude(user__id__in=members.values_list('user__id', flat=True))

                        possible = User.objects.filter(id__in=possible.values_list('user__id', flat=True))

                        members = User.objects.filter(id__in=members.values_list('user__id', flat=True))

                        return Response({
                            'members': UserSerializer(members, many=True).data,
                            'possible': UserSerializer(possible, many=True).data
                            },
                            status=status.HTTP_200_OK)
                    except CommunityGroup.DoesNotExist:
                        logger.error("Community Group does not exists")
                        pass

                except User.DoesNotExist:
                    logger.error("User does not exists")
                    pass
            except CommunityUser.DoesNotExist:
                logger.error("Community user does not exists")
                pass
        else:
            logger.error("User: " + user + " is not authenticated")
                
        #print "User: " + user + " is not authenticated"
        return  Response({}, status=status.HTTP_403_FORBIDDEN)
    
############################################################
##### Add user to a community group - Web service
############################################################


class CommunityGroupAddView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, community, group, email):

        if request.user.is_authenticated():
            try:
                cu = CommunityUser.objects.get(community__slug=community, user=request.user)
                try:
                    cuin = cu.community.owners.all().get(id=request.user.id)

                    try:
                        cg = CommunityGroup.valid(community = cu.community).get(id=int(group))

                        member = CommunityUser.objects.filter(community__slug = community, user__email=email)

                        if member.count() > 0:
                            cg.members.add(member[0])

                        return Response({
                            'success': True
                            },
                            status=status.HTTP_200_OK)
                    except CommunityGroup.DoesNotExist:
                        pass

                except User.DoesNotExist:
                    pass
            except CommunityUser.DoesNotExist:
                pass

        return  Response({}, status=status.HTTP_403_FORBIDDEN)


############################################################
##### Delete user to a community group - Web service
############################################################


class CommunityGroupDelView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, community, group, email):

        if request.user.is_authenticated():
            try:
                cu = CommunityUser.objects.get(community__slug=community, user=request.user)
                try:
                    cuin = cu.community.owners.all().get(id=request.user.id)

                    try:
                        cg = CommunityGroup.valid(community = cu.community).get(id=int(group))

                        member = CommunityUser.objects.filter(community__slug = community, user__email=email)

                        if member.count() > 0:
                            cg.members.remove(member[0])

                        return Response({
                            'success': True
                            },
                            status=status.HTTP_200_OK)
                    except CommunityGroup.DoesNotExist:
                        pass

                except User.DoesNotExist:
                    pass
            except CommunityUser.DoesNotExist:
                pass

        return  Response({}, status=status.HTTP_403_FORBIDDEN)


# Manage Groups 

class CommunityManageGroupView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, community):
        pass

    def post(self, request, community):
        if request.user.is_authenticated():
            try:
                logger.info("Community for slug: " + community)
                logger.info("User Id: " + str(request.user.id))

                # Check if the user has the correct permissions to do it in the community 
                cu = CommunityUser.objects.get(community__slug=community, user=request.user)
                cuin = cu.community.owners.all().get(id=request.user.id)
                
                # Only changes the differencial of the groups/plugins permissions 
                for key in request.data.keys():
                    if key.startswith('elem_'):
                        # Retrieve Id from request json 
                        kid = int(key[5:])
                        try:
                            # Fetch Community Permission 
                            cp = PluginPermission.objects.get(id=kid)
                            if request.data[key] == "true":
                                cp.allow = True
                            else:
                                cp.allow = False
                            cp.save()
                            
                        except PluginPermission.DoesNotExist:
                            # Jump 
                            logger.warn("*** PluginPermission.DoesNotExist ***")
                            pass
                return Response({
                            'success': True
                            },
                            status=status.HTTP_200_OK)

                
            except:
                # Not allowed or error 
                raise
        return  Response({}, status=status.HTTP_403_FORBIDDEN)


# Manage User Groups 
class CommunityManageUserGroupView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    parser_classes((JSONParser,))

    def get(self, request, community):
        pass

    def post(self, request, community):
        if request.user.is_authenticated():
            try:
                logger.info("Community for slug: " + community)
                logger.info("User Id: " + str(request.user.id))
                try:
                    community = Community.objects.get(slug=community)
                except Community.DoesNotExist:
                    return Response({"msg": "No community group found with given id"}, status=status.HTTP_404_NOT_FOUND)

                # Check if the user has the correct permissions to do it in the community 
                cu = CommunityUser.objects.get(community=community, user=request.user)
                owners = cu.community.owners.all()
                cuin = owners.get(id=request.user.id)  # if this raises an error then return 403

                # Only changes the differencial of the groups/plugins permissions 
                data = request.data['data']
                for key in data.keys():
                    if key.startswith('elem_'):
                        # Retrieve Id from request json 
                        
                        try:
                            kid = int(key[5:])
                            listUsers = data[key]

                            try:
                                cg = CommunityGroup.objects.get(community=community, pk=kid)
                            except CommunityGroup.DoesNotExist:
                                return Response(
                                    {"msg": "No community group found with id %d" % kid},
                                    status=status.HTTP_404_NOT_FOUND
                                )

                            if cg.name == CommunityGroup.DEFAULT_GROUP and community.membership == Community.MEMBERSHIP_OPEN:
                                # ignore changes on default group
                                continue
                            elif cg.name == CommunityGroup.DATABASE_OWNERS_GROUP:
                                # it doesn't make sense to add users to the database owners group
                                #  since we only use it on the context of a fingerprint. In this case
                                #  an user is in this group if is the owners (or shared owner) of
                                #  the database
                                continue

                            for userObj in listUsers:
                                try:
                                    email = userObj['email']
                                    active = userObj['value']

                                    try:
                                        tuser = community.communityuser_set.get(user__email=email)
                                    except CommunityUser.DoesNotExist:
                                        if community.membership == Community.MEMBERSHIP_OPEN:
                                            if active:
                                                try:
                                                    tuser = CommunityUser.objects.create(
                                                        community=community,
                                                        user=User.objects.get(email=email),
                                                        status=CommunityUser.ENABLED,
                                                    )

                                                    CommunityGroup.put_on_pre_existing_group(
                                                        CommunityGroup.DEFAULT_GROUP,
                                                        community,
                                                        tuser,
                                                    )
                                                except User.DoesNotExist:
                                                    return Response(
                                                        {"msg": "No user found with email %s" % email},
                                                        status=status.HTTP_404_NOT_FOUND
                                                    )

                                            else:
                                                # if the caller wants to remove this user from the current group
                                                #  and he doesn't have a community user record then ignore
                                                #  since he already in not in any group
                                                continue
                                        else:
                                            return Response(
                                                {"msg": "No community user found with email %s" % email},
                                                status=status.HTTP_404_NOT_FOUND
                                            )

                                    if active:
                                        cg.members.add(tuser)
                                    else:
                                        cg.members.remove(tuser)

                                        if community.membership == Community.MEMBERSHIP_OPEN \
                                                and tuser.user not in owners \
                                                and tuser.communitygroup_set.count() == 1:
                                            tuser.delete()
                                except Exception:
                                    logger.exception("Exception handling user on manage groups")
                            cg.save()
                        except Exception:
                            logger.exception("Exception handling group on manage groups")
                return Response({
                            'success': True
                            },
                            status=status.HTTP_200_OK)

                
            except:
                # Not allowed or error 
                raise
        return Response({}, status=status.HTTP_403_FORBIDDEN)

# Manage Groups 

class CommunityManageQSetsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, community):
        pass

    def post(self, request, community):
        if request.user.is_authenticated():
            try:
                logger.info("Community for slug: " + community)
                logger.info("User Id: " + str(request.user.id))

                # Check if the user has the correct permissions to do it in the community 
                # cu = CommunityUser.objects.get(community__slug=community, user=request.user)
                # cuin = cu.community.owners.all().get(id=request.user.id)
                qSetAGs = QuestionSetAccessGroups.objects.filter(communitygroup__community__slug=community)
                
                # Only changes the differencial of the groups/plugins permissions 
                for key in request.data.keys():
                    if key.startswith('elem_'):
                        r_or_w = key[5:]
                        kid = int(r_or_w[2:])
                        if r_or_w.startswith('r_'):
                            try:
                                qsAG = qSetAGs.get(id=kid)
                                if request.data[key] == "true":
                                    qsAG.can_read = True
                                else:
                                    qsAG.can_read = False
                                qsAG.save()
                                
                            except QuestionSetAccessGroups.DoesNotExist:
                                # Jump 
                                logger.warn("*** QuestionSetAccessGroups.DoesNotExist ***")
                                pass
                        elif r_or_w.startswith('w_'):
                            try:
                                qsAG = qSetAGs.get(id=kid)
                                if request.data[key] == "true":
                                    qsAG.can_write = True
                                else:
                                    qsAG.can_write = False
                                qsAG.save()
                            except QuestionSetAccessGroups.DoesNotExist:
                                logger.warn("*** QuestionSetAccessGroups.DoesNotExist ***")
                                pass
                return Response({
                            'success': True
                            },
                            status=status.HTTP_200_OK)

                
            except:
                # Not allowed or error 
                raise
        return  Response({}, status=status.HTTP_403_FORBIDDEN)


class CheckDeleteUserFromCommunityView(APIView):
    """
    Check if a given community user has fingerprints were he is the only owner.
    If it has, then we can't remove the user. A message should be displayed to the community
     manager saying that he must either delete or transfer the ownership of such fingerprints.
    """

    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, community, comm_user):
        if request.user.is_authenticated():
            try:
                comm = Community.objects.get(slug=community)
            except Community.DoesNotExist:
                pass
            else:
                if comm.is_owner(request.user) or request.user.is_superuser:
                    cu = get_object_or_404(comm.communityuser_set, id=int(comm_user))

                    single_owner_fps = comm\
                        .fingerprint_set\
                        .valid(owner=cu.user, include_drafts=True)\
                        .filter(shared=None, questionnaire__in=comm.questionnaires.all())

                    if single_owner_fps.exists():

                        data = dict()
                        for fp in single_owner_fps:
                            fp_data = {"hash": fp.fingerprint_hash, "name": fp.findName()}
                            if fp.questionnaire.name not in data:
                                data[fp.questionnaire.name] = [fp_data]
                            else:
                                data[fp.questionnaire.name].append(fp_data)

                        return JsonResponse({"allowed": False, "single_owner_fingerprints": data})
                    return JsonResponse({"allowed": True})

        return Response(status=status.HTTP_403_FORBIDDEN)
