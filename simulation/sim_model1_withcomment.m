clear all; close all; clc;
% Codes for ECS289F - "Opinion dynamics w/ reluctant agents"
% Feel free to play around with it...

N = 10;
A = ones(N) - eye(N); % This is a fully connected graph
iter_max = 2e3; % the max. no. of iterations 

flag = 0; % if flag = 0, run the standard reluctant agent model -> results in biased average
% if flag = 1, then the agents will "delay" until making the next update.
% In this case, the reluctant model will find the true average.

x0 = 10*rand(N,1); % Initialize the opinion with some random numbers..
x_avg = mean(x0); 

% Specify the adaptivity of the agents
tau_x = 2*ones(N,1); 
tau_x([1 2 5 8 10]) = 5; % select the reluctant agents

% Init. the algorithms
x_gossip = x0; x_model1 = x0; xh_model1 = x0; xo_model1 = x0;
cnt_xh = ones(N,1);
sq_dist_gos = zeros(iter_max,1); sq_dist_model1 = sq_dist_gos;

for iter_no = 1 : iter_max
    % A random node wake up at this time
    src_node = randint(1,1,[1 N]);
    % It selects a random neighbor with uniform probability
    pos_set = [1:src_node-1 src_node+1:N];
    pos_choice = find(A(src_node,pos_set)>0);
    dst_node_idx = randint(1,1,[1 length(pos_choice)]);
    dst_node = pos_choice(dst_node_idx);
    
    % Baseline: the two nodes communicates and update opinions instantly
    tmp_avg = (x_gossip(src_node) + x_gossip(dst_node))/2;
    x_gossip(src_node) = tmp_avg;
    x_gossip(dst_node) = tmp_avg;
    
    % For benchmarking: evaluate the square distance
    sq_dist_gos(iter_no) = sqrt(sum( (x_gossip-x_avg).^2 ));
    
    % Model 1 with reluctant agent
    cnt_xh = cnt_xh + 1;
    cnt_xh = min( tau_x, cnt_xh ); % such that the counter is bounded
    
    if ( (mod(iter_no,10) == 0) || (flag == 0) )
        cnt_xh(src_node) = 1; cnt_xh(dst_node) = 1; % reset the counters
        xo_model1(src_node) = x_model1(src_node); xo_model1(dst_node) = x_model1(dst_node);
        % tmp_avg is the average of the two agents' opinion
        tmp_avg = (x_model1(src_node) + x_model1(dst_node))/2;
        % xh_model1 corresponds to the \hat{x} in the writeup
        xh_model1(src_node) = tmp_avg; xh_model1(dst_node) = tmp_avg;
    end

    % we now evaluate the updates for both agents according to the
    % designed rule
    for n = 1 : N
        x_model1(n) = (cnt_xh(n)/tau_x(n))*xh_model1(n) + ...
            ((tau_x(n)-cnt_xh(n))/tau_x(n))*xo_model1(n);
    end
    
    % eval. the squared distance now
    sq_dist_model1(iter_no) = sqrt(sum( (x_model1-x_avg).^2 ));
end

fprintf('Sq. Dist to true average (baseline): %f ||',sq_dist_gos(end));
fprintf('Sq. Dist to true average (Model1): %f \n',sq_dist_model1(end));

semilogy(1:iter_max,sq_dist_gos,1:iter_max,sq_dist_model1)