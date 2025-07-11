from sqlalchemy.orm import Session
from networks.app.models import Users, Commercials, Networks, NetworkMembers


def assign_user_to_network(user_id: str, parranage_code: str, db: Session):
    # Retrieve the user by ID
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        return False, f"User with ID {user_id} not found."
    
    # Find the sponsor by referral code
    sponsor = db.query(Users).filter(Users.parranage_code == parranage_code).first()
    if not sponsor:
        raise Exception(f"Sponsor with referral code {parranage_code} not found.")
    
    # Check if the user is already in a network
    existing_member = db.query(NetworkMembers).filter(NetworkMembers.user_id == user_id).first()
    if existing_member:
        return False, f"User {user_id} is already a member of a network."
    
    # Check if sponsor belongs to a network
    sponsor_membership = db.query(NetworkMembers).filter(NetworkMembers.user_id == sponsor.id).first()
    if not sponsor_membership:
        return False, f"Sponsor {sponsor.id} does not belong to any network."

    network_id = sponsor_membership.network_id

    # Retrieve the sponsor's network details
    sponsor_network_info = db.query(Networks).filter(Networks.id == network_id).first()
    if not sponsor_network_info:
        return False, "Sponsor's network not found."
    
    # If the network is full, create a new one
    if sponsor_network_info.total_members >= sponsor_network_info.max_members:
        new_network = Networks(
            commercial_id=sponsor_network_info.commercial_id,
            plan_type="5:4",  # This can be dynamically configured
            status="Active",
            total_members=0
        )
        db.add(new_network)
        db.commit()
        db.refresh(new_network)
        network_id = new_network.id
    else:
        network_id = sponsor_network_info.id
    
    # Get sponsor info in the specific network
    sponsor_info = db.query(NetworkMembers).filter(
        NetworkMembers.user_id == sponsor.id,
        NetworkMembers.network_id == network_id
    ).first()

    if not sponsor_info:
        raise Exception("Sponsor is not a member of the network.")

    generation = sponsor_info.generation + 1

    # Count how many people the sponsor has already referred in this generation
    position_in_generation = (
        db.query(NetworkMembers)
        .filter(
            NetworkMembers.network_id == network_id,
            NetworkMembers.sponsor_id == sponsor.id,
            NetworkMembers.generation == generation
        )
        .count()
    ) + 1

    # Add the user to the network
    network_member = NetworkMembers(
        network_id=network_id,
        user_id=user.id,
        sponsor_id=sponsor.id,
        generation=generation,
        position_in_generation=position_in_generation
    )
    db.add(network_member)

    # Update the total members of the network
    sponsor_network_info.total_members += 1
    db.commit()

    return True, f"User {user.id} was successfully added to the network."


def calculate_generation_and_position(db: Session, network_id: str, plan_type: str):
    # Retrieve all members in the network
    members = db.query(NetworkMembers).filter(NetworkMembers.network_id == network_id).all()

    # Split the plan type to get generation rules
    generations = plan_type.split(":")  # Example: "5:4" → ['5', '4']

    if len(generations) != 2:
        raise ValueError(f"Invalid network plan: {plan_type}. Expected format 'X:Y'.")

    first_gen_size = int(generations[0])
    other_gen_multiplier = int(generations[1])

    # Calculate the size of each generation
    generation_count = {}
    for g in range(1, 5):
        if g == 1:
            generation_count[g] = first_gen_size
        else:
            generation_count[g] = generation_count[g - 1] * other_gen_multiplier

    generation = 1
    position_in_generation = 0

    for g in range(1, 5):
        members_in_generation = [m for m in members if m.generation == g]
        if len(members_in_generation) < generation_count[g]:
            generation = g
            position_in_generation = len(members_in_generation) + 1
            break

    return generation, position_in_generation


def create_and_add_commercial_to_network(commercial_id: str, db: Session):
    # Retrieve the commercial by ID
    commercial = db.query(Commercials).filter(Commercials.id == commercial_id).first()
    if not commercial:
        return False, f"Commercial with ID {commercial_id} not found."

    # Create a new network for the commercial
    new_network = Networks(
        commercial_id=commercial.id,
        plan_type="5:4",
        status="Active",
        total_members=1
    )
    db.add(new_network)
    db.commit()
    db.refresh(new_network)

    # Add the commercial as the first member of their own network
    network_member = NetworkMembers(
        network_id=new_network.id,
        user_id=commercial.user_id,
        sponsor_id=commercial.user_id,
        generation=1,
        position_in_generation=1
    )
    db.add(network_member)
    db.commit()

    return True, f"Network for commercial {commercial.id} was successfully created."


def get_user_network_tree(user_id: str, db: Session):
    # Check if the user exists
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        return {}

    # Check if the user is part of a network
    user_network = db.query(NetworkMembers).filter(NetworkMembers.user_id == user_id).first()
    if not user_network:
        return {}

    # Retrieve all network members in one query
    network_members = db.query(NetworkMembers).filter(
        NetworkMembers.network_id == user_network.network_id
    ).all()

    # Build a mapping of user_id to their generation info
    member_info_map = {
        member.user_id: {
            "generation": member.generation,
            "position_in_generation": member.position_in_generation,
            "sponsor_id": member.sponsor_id
        }
        for member in network_members
    }

    # Get all commercial user IDs
    commercial_user_ids = set(
        db.query(Commercials.user_id)
        .join(Networks, Commercials.id == Networks.commercial_id)
        .all()
    )
    commercial_user_ids = {id for (id,) in commercial_user_ids}

    # Retrieve all user details for network members
    users = db.query(Users).filter(
        Users.id.in_([m.user_id for m in network_members])
    ).all()

    user_dict = {}
    for u in users:
        info = member_info_map.get(u.id, {})
        user_dict[u.id] = {
            "name": u.name or u.username or "Unknown",
            "is_head": u.id in commercial_user_ids,
            "generation": info.get("generation"),
            "position_in_generation": info.get("position_in_generation"),
        }

    # Organize members by sponsor
    members_by_sponsor = {}
    for member in network_members:
        if member.sponsor_id not in members_by_sponsor:
            members_by_sponsor[member.sponsor_id] = []
        members_by_sponsor[member.sponsor_id].append(member)

    # Recursive function to build the network tree
    def build_tree(user_id, visited=set()):
        if user_id in visited:
            return {"error": "Cycle detected!"}

        visited.add(user_id)

        user_info = user_dict.get(user_id, {
            "name": "Unknown",
            "is_head": False,
            "generation": None,
            "position_in_generation": None
        })

        node = {
            "user_id": user_id,
            "name": user_info["name"],
            "is_head": user_info["is_head"],
            "generation": user_info["generation"],
            "position_in_generation": user_info["position_in_generation"],
            "children": []
        }

        for child in members_by_sponsor.get(user_id, []):
            child_node = build_tree(child.user_id, visited.copy())
            if child_node:
                node["children"].append(child_node)

        return node

    # Build and return the full network tree
    return build_tree(user_id)
